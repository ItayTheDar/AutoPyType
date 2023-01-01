# type hinting:
from inverted_index_gcp import InvertedIndex, MultiFileReader
import struct
import time
import os
from google.cloud import storage
from contextlib import closing
import pickle as pkl
from typing import List, Tuple


class ReadPostingsCloud:
    """A class for reading postings from the cloud"""

    def __init__(self, bucket_name: str):
        # size constant for reading postings
        self.TUPLE_SIZE: int = 6
        self.TUPLE_SIZE_BODY: int = 8
        self.TF_MASK: int = 2 ** 16 - 1  # Masking the 16 low bits of an integer
        # google cloud elements
        self.client: storage.Client = storage.Client()
        self.bucket: storage.bucket.Bucket = self.client.get_bucket(bucket_name)

    def download_from_buck(self, source: str, dest: str):
        """
        Download file from Google cloud storage bucket

        :param source: source file name (in the bucket)
        :param dest: destination file name 
        """
        blob: storage.blob.Blob = self.bucket.get_blob(source)
        blob.download_to_filename(dest)

    def get_pickle_file(self, source: str, dest: str) -> dict:
        """
        Download file from Google cloud storage bucket and load it using pickle

        :param source: source file name (in the bucket)
        :param dest: destination file name 
        :return: the pickled file
        """
        if dest not in os.listdir("."):
            self.download_from_buck(source, dest)

        # open the file in binary read mode
        with open(dest, "rb") as f:
            return pkl.load(f)

    def get_inverted_index(self, source_idx: str, dest_file: str) -> InvertedIndex:
        """
        Download the inverted rile from Google cloud storage and return an InvertedIndex file

        :param source_idx: source file name (in the bucket)
        :param dest_file: destination file name 
        :return: an InvertedIndex object
        """
        self.download_from_buck(source_idx, dest_file)
        return InvertedIndex().read_index(".", dest_file.split(".")[0])

    def read_posting_list(self, inverted: InvertedIndex, w: str,
                          index_name: str, isBody: bool = False, is_production: bool = False) -> List[
        Tuple[int, float]]:
        """
        Read the posting list of word w from the inverted index


        :param inverted: an InvertedIndex object
        :param w: the word 
        :param index_name: name of the index
        :param isBody: if true return tfidf insteand of raw tf
        :param is_production: running in production mod?
        :return: a posting list 
        """
        s: float = time.time()
        try:
            with closing(MultiFileReader()) as reader:
                locs: List[Tuple[str, int]] = inverted.posting_locs[w]
                if is_production:
                    locs = list(
                        map(
                            lambda x: (f"postings_gcp_{index_name}/{x[0]}", x[1]),
                            locs
                        )
                    )
                else:
                    for loc in locs:
                        if loc[0] not in os.listdir("."):
                            blob: storage.blob.Blob = self.bucket.get_blob(f"postings_gcp_{index_name}/{loc[0]}")
                            filename: str = f"{blob.name.split('/')[-1]}"
                            blob.download_to_filename(filename)
                posting_list: List[Tuple[int, float]] = []
                if isBody:
                    b: bytes = reader.read(locs, inverted.df[w] * self.TUPLE_SIZE_BODY)
                    for i in range(inverted.df[w]):
                        try:
                            doc_id, tfidf = struct.unpack("If",
                                                          b[i * self.TUPLE_SIZE_BODY: (i + 1) * self.TUPLE_SIZE_BODY])
                            posting_list.append((doc_id, tfidf))
                        except Exception as e:
                            continue
                else:
                    b: bytes = reader.read(locs, inverted.df[w] * self.TUPLE_SIZE)
                    for i in range(inverted.df[w]):
                        doc_id: int = int.from_bytes(b[i * self.TUPLE_SIZE:i * self.TUPLE_SIZE + 4], 'big')
                        tf: int = int.from_bytes(b[i * self.TUPLE_SIZE + 4:(i + 1) * self.TUPLE_SIZE], 'big')
                        posting_list.append((doc_id, tf))
                print(time.time() - s)
                return posting_list
        except IndexError:
            return []


# adding logs:
from inverted_index_gcp import InvertedIndex, MultiFileReader
import struct
import time
import os
from google.cloud import storage
from contextlib import closing
import pickle as pkl
from typing import List, Tuple
import logging


class ReadPostingsCloud:
    """A class for reading postings from the cloud"""
    # initializes the logger
    logger = logging.getLogger(__name__)
    logger.setLevel(logging.INFO)
    formatter = logging.Formatter('%(asctime)s:%(name)s:%(levelname)s:%(message)s')

    file_handler = logging.FileHandler('read_postings_cloud.log')
    file_handler.setFormatter(formatter)

    logger.addHandler(file_handler)

    def __init__(self, bucket_name: str):
        # size constant for reading postings
        self.TUPLE_SIZE: int = 6
        self.TUPLE_SIZE_BODY: int = 8
        self.TF_MASK: int = 2 ** 16 - 1  # Masking the 16 low bits of an integer
        # google cloud elements
        self.client: storage.Client = storage.Client()
        self.bucket: storage.bucket.Bucket = self.client.get_bucket(bucket_name)

    def download_from_buck(self, source: str, dest: str):
        """
        Download file from Google cloud storage bucket
        
        :param source: source file name (in the bucket)
        :param dest: destination file name 
        """
        self.logger.info(f" beginning to download file {source} to {dest}")
        blob: storage.blob.Blob = self.bucket.get_blob(source)
        blob.download_to_filename(dest)
        self.logger.info(f"  Finish downloading file {source} to {dest}")

    def get_pickle_file(self, source: str, dest: str) -> dict:
        """
        Download file from Google cloud storage bucket and load it using pickle

        :param source: source file name (in the bucket)
        :param dest: destination file name 
        :return: the pickled file
        """
        self.logger.info(f" downloading from {source} to local {dest}")
        if dest not in os.listdir("."):
            self.download_from_buck(source, dest)

        # open the file in binary read mode
        self.logger.info(f" loading pickle file from {dest}")
        with open(dest, "rb") as f:
            return pkl.load(f)

    def get_inverted_index(self, source_idx: str, dest_file: str) -> InvertedIndex:
        """
        Download the inverted rile from Google cloud storage and return an InvertedIndex file

        :param source_idx: source file name (in the bucket)
        :param dest_file: destination file name 
        :return: an InvertedIndex object
        """
        self.logger.info(f" Downloading inv index from {source_idx} to {dest_file}")
        self.download_from_buck(source_idx, dest_file)
        self.logger.info(f"  Finish downloading inv index from {source_idx} to {dest_file}")
        self.logger.info(f" Reading index {dest_file.split('.')[0]}")
        return InvertedIndex().read_index(".", dest_file.split(".")[0])

    def read_posting_list(self, inverted: InvertedIndex, w: str,
                          index_name: str, isBody: bool = False,
                          is_production: bool = False) -> List[Tuple[int, float]]:
        """
        Read the posting list of word w from the inverted index

        :param inverted: an InvertedIndex object
        :param w: the word 
        :param index_name: name of the index
        :param isBody: if true return tfidf insteand of raw tf
        :param is_production: running in production mod?
        :return: a posting list 
        """
        s: float = time.time()
        self.logger.info(f"reading posting list for word {w}")
        try:
            with closing(MultiFileReader()) as reader:
                locs: List[Tuple[str, int]] = inverted.posting_locs[w]
                if is_production:
                    locs = list(
                        map(
                            lambda x: (f"postings_gcp_{index_name}/{x[0]}", x[1]),
                            locs
                        )
                    )
                else:
                    for loc in locs:
                        if loc[0] not in os.listdir("."):
                            blob: storage.blob.Blob = self.bucket.get_blob(f"postings_gcp_{index_name}/{loc[0]}")
                            filename: str = f"{blob.name.split('/')[-1]}"
                            blob.download_to_filename(filename)
                posting_list: List[Tuple[int, float]] = []
                if isBody:
                    b: bytes = reader.read(locs, inverted.df[w] * self.TUPLE_SIZE_BODY)
                    self.logger.info(f"reading postings on isBody mod")
                    for i in range(inverted.df[w]):
                        try:
                            doc_id, tfidf = struct.unpack("If",
                                                          b[i * self.TUPLE_SIZE_BODY: (i + 1) * self.TUPLE_SIZE_BODY])
                            posting_list.append((doc_id, tfidf))
                        except Exception as e:
                            self.logger.warning(f"could not unpack {i}th data entry")
                            continue
                else:
                    b: bytes = reader.read(locs, inverted.df[w] * self.TUPLE_SIZE)
                    self.logger.info(f"reading postings")
                    for i in range(inverted.df[w]):
                        doc_id: int = int.from_bytes(b[i * self.TUPLE_SIZE:i * self.TUPLE_SIZE + 4], 'big')
                        tf: int = int.from_bytes(b[i * self.TUPLE_SIZE + 4:(i + 1) * self.TUPLE_SIZE], 'big')
                        posting_list.append((doc_id, tf))
                self.logger.info(f"finish reading postings, took {time.time() - s}")
                return posting_list
        except IndexError:
            self.logger.info(f"could not find postings for {w}")
            return []


# adding documentation:

from inverted_index_gcp import InvertedIndex, MultiFileReader
import struct
import time
import os
from google.cloud import storage
from contextlib import closing
