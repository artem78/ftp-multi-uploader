from threading import Thread, RLock#, Lock
from queue import Queue
from ftplib import FTP
import logging
from os.path import basename


class _FTPMultiUploaderWorker(Thread):

    def __init__(self, host, port, login, password, directory, upload_callback, files_queue, lock):
        super().__init__()

        self._host = host
        self._port = port
        self._login = login
        self._password = password
        self._directory = directory
        self._upload_callback = upload_callback
        self._files_queue = files_queue
        self._lock = lock

        self._ftp = FTP()

    def run(self):
        logging.debug('Thread %s started', self.name)

        self._ftp_connect()

        try:
            while not self._files_queue.empty():
                file = self._files_queue.get()
                try:
                    self._upload_file(file)
                except Exception as e:
                    logging.exception('Error while uploading file %s', file)
                    is_success = False
                    #raise e
                else:
                    is_success = True
                finally:
                    with self._lock:
                        self._upload_callback(file, is_success)

                    self._files_queue.task_done()

        except Exception as e:
            logging.exception('Thread exited with error')
        finally:
            self._ftp_disconnect()

        logging.debug('Thread %s finished', self.name)

    def _upload_file(self, file):
        filename = basename(file)
        logging.debug('Start uploading file %s', filename)
        with open(file, 'rb') as fobj:
            self._ftp.storbinary('STOR ' + filename, fobj)
        logging.info('File %s sucessfully uploaded', filename)

    def _ftp_connect(self):
        self._ftp.connect(self._host, self._port)
        self._ftp.login(self._login, self._password)
        logging.debug('Connected to FTP')
        self._ftp.cwd(self._directory)

    def _ftp_disconnect(self):
        self._ftp.quit()
        logging.debug('FTP connection closed')


class FTPMultiUploader():

    def __init__(self, host, port, login, password, directory='/', threads_count=3, upload_callback=lambda file, is_success: None):
        self._host = host
        self._port = port
        self._login = login
        self._password = password
        self._directory = directory

        self._threads_count = threads_count
        self._upload_callback = upload_callback

        self._files_queue = Queue()
        self._lock = RLock()

    def add_file(self, file):
        self._files_queue.put(file)

    def run(self):
        if self._files_queue.empty():
            return

        threads = []
        for i in range(self._threads_count):
            thr = _FTPMultiUploaderWorker(
                host=self._host,
                port=self._port,
                login=self._login,
                password=self._password,
                directory=self._directory,
                upload_callback=self._upload_callback,
                files_queue=self._files_queue,
                lock=self._lock
            )
            thr.start()
            threads.append(thr)

        for thr in threads:
            thr.join()
