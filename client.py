import asyncio


class Client:
    def __init__(self, host: str, port: int) -> None:
        self.host = host
        self.port = port

    @staticmethod
    async def receiver(reader, writer):
        while True:
            data = await reader.read(1000)
            if not data:
                print('Server is offline.')
                break
            print(f'{data.decode("utf-8")}')
            if data.decode("utf-8") == (
                'Close connection: Idle timeout expired.'
            ):
                break
        writer.close()

    @staticmethod
    async def sender(writer):
        while True:
            data = await asyncio.get_event_loop().run_in_executor(
                None,
                input,
            )
            writer.write(data.encode('utf-8'))

    async def main(self):
        try:
            reader, writer = await asyncio.open_connection(
                self.host,
                self.port
            )
            task_receive = asyncio.get_event_loop().create_task(
                self.receiver(
                    reader,
                    writer
                )
            )
            task_send = asyncio.get_event_loop().create_task(
                self.sender(writer)
            )
            await task_receive
            await task_send
        except ConnectionRefusedError:
            print('This server is offline.')


if __name__ == '__main__':
    host = input('Укажите адрес сервера: ')
    port = input('Укажите порт подключения: ')
    client = Client(host, port)
    asyncio.run(client.main())
