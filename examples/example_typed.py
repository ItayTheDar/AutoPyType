#Answer:
import logging
from typing import Tuple, List
import struct
import time
import os
from google.cloud import storage
from contextlib import closing
import pickle as pkl

from inverted_index_gcp import InvertedIndex, MultiFileReader


class ReadPostingsCloud:

    TUPLE_SIZE: int
    TUPLE_SIZE_BODY: int
    TF_MASK: int
    client: storage.Client
    bucket: storage.Bucket

    def __init__(self, bucket_name: str):
        self.TUPLE_SIZE = 6
        self.TUPLE_SIZE_BODY = 8
        self.TF_MASK = 2 ** 16 - 1  # Masking the 16 low bits of an integer
        self.client = storage.Client()
        self.bucket = self.client.get_bucket(bucket_name)

    def download_from_buck(self, source: str, dest: str):
        """Download file from a Google Cloud bucket.
        
        Args:
            source (str): Source file in cloud.
            dest (str): Destination for downloaded file.
        """
        blob = self.bucket.get_blob(source)
        blob.download_to_filename(dest)

        logging.info("Downloaded {} to {}".format(source, dest))

    def get_pickle_file(self, source: str, dest: str) -> object:
        """Download pickle file from a Cloud bucket.
        
        Args:
            source (str): Source file in cloud.
            dest (str): Destination for downloaded file.
        
        Returns:
            object: A python object stored in the pickle file.
        """
        if dest not in os.listdir("."):
            self.download_from_buck(source, dest)

        with open(dest, "rb") as f:
            py_obj = pkl.load(f)
            logging.info("Loaded pickle file from {}".format(dest))
            return py_obj

    def get_inverted_index(self, source_idx: str, dest_file: str):
        """Download inverted index posting file from a Cloud bucket and reconstruct the index.
        
        Args:
            source_idx (str): Source file in cloud.
            dest_file (str): Destination for downloaded file.
        
        Returns:
            InvertedIndex: The inverted index.
        """
        self.download_from_buck(source_idx, dest_file)
        idx = InvertedIndex().read_index(".", dest_file.split(".")[0])

        logging.info("Reconstructed index from {} to {}".format(source_idx, dest_file))
        return idx

    def read_posting_list(self, inverted: InvertedIndex, w: str,
                          index_name: str, isBody: bool = False,
                          is_production: bool = False
                         ) -> List[Tuple[int, int]]:
        """Read posting list from an Inverted Index. 

        Args:
            inverted (InvertedIndex): The inverted index.
            w (str): The word for which to read the posting list.
            index_name (str): Name of the inverted index.
            isBody (bool): Determine if we are use the body indices or location indices (default is False).
            is_production (bool): True if the index is hosted in cloud. False, otherwise.
        
        Returns:
            List[Tuple[int, int]]: The posting list.
        """
        s = time.time()

        try:
            with closing(MultiFileReader()) as reader:
                locs = inverted.posting_locs[w]

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
                            blob = self.bucket.get_blob(f"postings_gcp_{index_name}/{loc[0]}")
                            filename = f"{blob.name.split('/')[-1]}"
                            blob.download_to_filename(filename)
                posting_list = []
                
                if isBody:
                    b = reader.read(locs, inverted.df[w] * self.TUPLE_SIZE_BODY)
                    for i in range(inverted.df[w]):
                        try:
                            doc_id, tfidf = struct.unpack("If",
                                                    b[i * self.TUPLE_SIZE_BODY: (i + 1) * self.TUPLE_SIZE_BODY])
                            posting_list.append((doc_id, tfidf))
                        except Exception as e:
                            logging.error('Exception {} occurred'.format(e))
                            continue
                else:
                    b = reader.read(locs, inverted.df[w] * self.TUPLE_SIZE)
                    for i in range(inverted.df[w]):
                        doc_id = int.from_bytes(b[i * self.TUPLE_SIZE:i * self.TUPLE_SIZE + 4], 'big')
                        tf = int.from_bytes(b[i * self.TUPLE_SIZE + 4:(i + 1) * self.TUPLE_SIZE], 'big')
                        posting_list.append((doc_id, tf))
                
                logging.info('Read postings list from inverted index in {}s'.format(time.time() - s))
                return posting_list
        except IndexError:
            return []