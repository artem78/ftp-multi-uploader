Introduction
============

This module upload files to ftp server using several threads.

Usage
=====

```python
from FTPMultiUploader import FTPMultiUploader


def upload_callback(file, is_success):
    print('file {} {}!'.format(file, 'uploaded' if is_success else 'failed'))


ftp = FTPMultiUploader(
    host='127.0.0.1',
    port=21,
    login='ftpuser',
    password='123456',
    directory='/testdir/',
    threads_count=3,
    upload_callback=upload_callback
)

ftp.add_file('/path/to/dir/file1.jpg')
ftp.add_file('/path/to/dir/file2.jpg')
ftp.add_file('/path/to/dir/file3.jpg')
ftp.add_file('/path/to/dir/file4.jpg')
ftp.add_file('/path/to/dir/file5.jpg')

ftp.run() # Start uploading selected files  
```