import grpc
import file_pb2
import file_pb2_grpc
import os
from flask import Flask, send_file, request
from concurrent import futures
import environs

env = environs.Env()
env.read_env()
print(f"Public: '{env('PUBLIC_SERVER_IP')}'")
print(f"Private: '{env('GRPC_SERVER_IP')}'")
print(f"Backup: '{env('BACKUP')}'")

_ONE_DAY_IN_SECONDS = 60 * 60 * 24
CHUNK_SIZE = 1024 * 1024  # 1MB
MESSAGE_SIZE = 1024 * 1024 * 10 * 2

app = Flask(__name__)

class FileService(file_pb2_grpc.FileServiceServicer):
    """
    Servidor del servicio de 
  
    """
    def ListFiles(self, request, context):
        """Servicio de  listar los archivos
        Esta versión se quedo sin namespacear

        Args:
            request : ¯\_(ツ)_/¯
            context : sirve para el manejo de errores

        Returns:
            file_pb2.ListFilesResponse: Lista de nombres de archivos
        """
        try:
            files = []
            # FIXME Dizque "." gas
            for file in os.listdir("."):
                if os.path.isfile(file):
                    files.append(file)
            return file_pb2.ListFilesResponse(filenames=files)

        except Exception as e:
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details(f"Error listing files: '{str(e)}'")

    def ReplicateFile(self, request_iterator, context):
        """Replicación cutre, donde cada dataNode trata de replicar el archivo
        apenas llega en el servidor asignado en el .env

        Según me acuerdo funcionó con archivos lo suficientemente grandes
        it fucking worked leave me alone.

        Si hubieramos usado Zookeeper probablemente nos hubieramos evitado tener hacer esta salvajada

        Args:
            request_iterator (_type_): ಠಿ_ಠ
            context (_type_): para manejo de errores

        Returns:
            _type_: _description_
        """
        try:
            filename = ""
            file_content = b""
            # Accumulate file content
            for chunk in request_iterator:
                if not filename:
                    filename = chunk.filename
                file_content += chunk.content

            # Save the received file content to a new file
            # When there is naming conflict it overwrites
            with open(filename, "ab") as file:
                file.write(file_content)

            return file_pb2.ReplicateResponse(
                message=f"File '{filename}' replicated successfully"
            )

        except Exception as e:
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details(f"Error replicating file: '{str(e)}'")


@app.route("/download/<filename>", methods=["GET"])
def download_http_file(filename):
    """Ya le doy lo que me pidió


    Args:
        filename (_type_): diga que quiere

    Returns:
        _type_: ``return flask.send_file(filename, as_attachment=True)`` o algo
    """
    try:
        if not os.path.isfile(filename):
            return "File not found", 404
        
        return send_file(filename, as_attachment=True)
    except Exception as e:
        return f"Error downloading file: '{str(e)}'", 500


@app.route("/upload/<filename>", methods=["POST"])
def upload_file(filename):
    """Aquí se guarda el archivo subido al servidor y se replica de manera bloqueante

    Args:
        filename (str): file name

    Returns:
        str: Completion status
    """
    try:
        file_data = request.data
        # Save the file to the filesystem
        with open(filename, "wb") as f:
            f.write(file_data)
        print("A punto de replicar archivo")
        with grpc.insecure_channel(
            f"{env('BACKUP')}:50051",
            options=[
                ("grpc.max_send_message_length", MESSAGE_SIZE),
                ("grpc.max_receive_message_length", MESSAGE_SIZE),
            ],
        ) as channel:
            stub = file_pb2_grpc.FileServiceStub(channel)

            # Open the file for reading, read from it while sending it to network
            # Not exactly zero-copy pero file.read creo que al menos no mete todo el archivo en el proceso 
            # Uno no cree que eso vaya a servir hasta que empieza a meter archivos de 4 Gb en un EC2 con 2 Gb 
            # RAM entonces no quiero quejas aquí tampoco
            with open(filename, "rb") as file:
                chunk_size = CHUNK_SIZE
                while True:
                    chunk = file.read(chunk_size)
                    if not chunk:
                        break
                    grpc_request = file_pb2.ReplicateRequest(
                        filename=filename, content=chunk
                    )
                    response = stub.ReplicateFile(iter([grpc_request]))

            print(response.message)
            print("File replicated successfully")

            return "File uploaded and replicated successfully!"
    except Exception as e:
        return f"Error uploading and replicating file: '{str(e)}'", 500


def serve():
    """
    Inicia servidor de grpc y Flask
    """
    server = grpc.server(
        futures.ThreadPoolExecutor(max_workers=10),
        options=[
            ("grpc.max_send_message_length", MESSAGE_SIZE),
            ("grpc.max_receive_message_length", MESSAGE_SIZE),
        ],
    )
    file_pb2_grpc.add_FileServiceServicer_to_server(FileService(), server)
    address = f"{env('GRPC_SERVER_IP')}:50051"
    server.add_insecure_port(address)
    server.start()

    print(f"gRPC Server started on '{address}'")


    # Start the Flask app for HTTP downloads
    app.run(host=env("GRPC_SERVER_IP"), port=8080)  # Listen on all network interfaces


if __name__ == "__main__":
    serve()
