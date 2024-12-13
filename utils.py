import os
import boto3
from io import BytesIO

def copy_from_ec2_to_local(ec2_public_ip:str, source:str, destination:str = r"C:\\Users\\RoozbehKoochak\\Documents", 
                           f_type:str='dir'):
    r""" Returns the command to copy from ec2 to local

    Args:
        ec2_public_ip (str): to get from AWS (this changes everytime the instance is stopped)
        source (str): the file or folder that needs to be copied from EC@
        destination (_type_, optional): location to copy to. Defaults to 'C:\Users\RoozbehKoochak\Documents'.
        f_type (str, optional): can be either 'file' or 'dir'. Defaults to 'dir'.

    Returns:
        str: the scp command to copy data from Ec2. the command to be run in local shell.
    """    
    key_file = r"c:\Users\RoozbehKoochak\.ssh\Rooz_server_key.pem"
    if f_type=='file':
        command = print(f'scp -i "{key_file}" ubuntu@{ec2_public_ip}:{source} {destination}')
    else:
        command = print(f'scp -i "{key_file}" -r ubuntu@{ec2_public_ip}:{source} {destination}')
    return command

def copy_from_local_to_ec2(ec2_public_ip:str, source:str, destination:str, 
                           f_type:str='file')->str:
    """copies a local file or folder to a destination in EC@

    Args:
        ec2_public_ip (str): get from AWS (this changes everytime the instance is stopped)
        source (str): the file or folder that needs to be copied from local
        destination (str): location to copy to.
        f_type (str, optional): can be either 'file' or 'dir'. Defaults to 'file'.

    Returns:
        str: _description_
    """    
    key_file = r"c:\Users\RoozbehKoochak\.ssh\Rooz_server_key.pem"
    if f_type=='file':
        command = print(f'scp -i "{key_file}" {source} ubuntu@{ec2_public_ip}:{destination}')
    else:
        command = print(f'scp -i "{key_file}" -r {source} ubuntu@{ec2_public_ip}:{destination}')
    return command

class Read_S3_Data():
    def __init__(self, bucket_name, folder_prefix = ''):
        """To initiate an S3 object, provide a Bucket Name and a folder prefix.

        Args:
            bucket_name (str): Bucket name in strng quotaions
            folder_prefix (str, optional): _description_. Defaults to ''.
        """
        self.bucket_name = bucket_name
        self.folder_prefix = folder_prefix
        self.session = boto3.Session(profile_name='default')
        self.s3 = self.session.client('s3')
        
    def list_content(self) -> list: 
        paginator = self.s3.get_paginator('list_objects_v2') # the paginator is required becasue by default the 'list_objects_v2' returns first 1000 files only.
        pages = paginator.paginate(Bucket=self.bucket_name, Prefix=self.folder_prefix)
        self.file_list = [obj['Key'] for page in pages for obj in page['Contents']]
        return self.file_list
    
    def list_by_ftype(self, ftype: str) -> list:
        """return all the files with a specific type recursively under a folder_prefix
        Args:
            ftype (str): input string without the '.'

        Returns:
            list: list of all the availabel files of the above type in the folder prefix
        """
        paginator = self.s3.get_paginator('list_objects_v2') # the paginator is required becasue by default the 'list_objects_v2' returns first 1000 files only.
        pages = paginator.paginate(Bucket=self.bucket_name, Prefix=self.folder_prefix)
        self.ftype_list = [obj['Key'] for page in pages for obj in page['Contents'] if obj['Key'].split('.')[-1] == ftype]  # this is a nested for loop, try and find a faster way of implementing it.
        
        return self.ftype_list
    
    def get_file_binary(self, fname: str):
        """This function takes in the S3 bucket key of a file and returns the file in buffer format.

        Args:
            fname (str): full s3 bucket key

        Returns:
            BytesIO: buffer format of the file.
        """
        # self.list_response = self.s3.list_objects_v2(Bucket=self.bucket_name, Prefix=self.folder_prefix)
        key = fname#[cont['Key'] for cont in self.list_response['Contents'] if cont['Key'].split('/')[-1] == fname][0]
        response = self.s3.get_object(Bucket = self.bucket_name, Key = key)
        return BytesIO(response['Body'].read())
    
    def get_file_s3_object(self, fname: str):
        """_summary_

        Args:
            fname (str): _description_

        Returns:
            _type_: _description_
        """    
        self.list_response = self.s3.list_objects_v2(Bucket=self.bucket_name, Prefix=self.folder_prefix)
        key = [cont['Key'] for cont in self.list_response['Contents'] if cont['Key'].split('/')[-1] == fname][0]
        document={
            'Bucket': self.bucket_name,
            'Key': key
        }
        return document
    
    def download_s3_file(self, f_name:str,dest:str):
        """Downloads file object from s3 to a destination file name.

        Args:
            f_name (str): object file name
            dest (str): destination address including the file name
        """        
        f_key = self.get_file_s3_object(fname=f_name)['Key']
        self.s3.download_file(self.bucket_name,f_key,dest)


    
def download_s3_folder(s3, bucket_name, s3_folder, local_dir=None):
    """
    Download the contents of a folder directory
    Args:
        s3: It is initiated as s3 = boto3.client('s3')
        bucket_name: the name of the s3 bucket
        s3_folder: the folder path in the s3 bucket
        local_dir: a relative or absolute directory path in the local file system
    """
    os.makedirs(local_dir, exist_ok=True)

    bucket = s3.Bucket(bucket_name)
    for obj in bucket.objects.filter(Prefix=s3_folder):
        target = obj.key if local_dir is None \
            else os.path.join(local_dir, os.path.relpath(obj.key, s3_folder))
        if not os.path.exists(os.path.dirname(target)):
            os.makedirs(os.path.dirname(target))
        if obj.key[-1] == '/':
            continue
        bucket.download_file(obj.key, target)
        
def scp_to_ec2(public_ip:str, source:str, destination:str, type:str='file')->str:
    """Generates an SCP command string to copy files to an EC2 instance.

    Args:
    - public_ip (str): The public IP address of the EC2 instance.
    - source (str): The local path to the file or directory to copy.
    - destination (str): The destination path on the EC2 instance.
    - type (str, optional): command for 'file' or 'dir'. Defaults to 'file'.

    Returns:
    - str: The SCP command string.
    """    
    key_path = r"C:\Users\RoozbehKoochak\.ssh\Rooz_server_key.pem"
    if type == 'file':
        command = f'scp -i "{key_path}" "{source}" ubuntu@{public_ip}:"{destination}"'
    else:
        command = f'scp -i -r "{key_path}" "{source}" ubuntu@{public_ip}:"{destination}"'
    return command    

def scp_to_local(public_ip:str, source:str, destination:str, type:str='file')->str:
    """Generates an SCP command string to copy files from an EC2 instance to local.

    Args:
    - public_ip (str): The public IP address of the EC2 instance.
    - source (str): The local path to the file or directory to copy.
    - destination (str): The destination path on the local.
    - type (str, optional): command for 'file' or 'dir'. Defaults to 'file'.

    Returns:
    - str: The SCP command string.
    """    
    key_path = r"C:\Users\RoozbehKoochak\.ssh\Rooz_server_key.pem"
    if type == 'file':
        command = f'scp -i "{key_path}" ubuntu@{public_ip}:"{source}" "{destination}"'
    else:
        command = f'scp -i -r "{key_path}" ubuntu@{public_ip}:"{source}" "{destination}"'
    return command    
    