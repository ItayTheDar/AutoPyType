from inverted_index_gcp import InvertedIndex, MultiFileReader
import struct
import time
import os
from google.cloud import storage
from contextlib import closing
import pickle as pkl
from typing import List, Tuple


class ReadPostingsCloud:
    TUPLE_SIZE: int = 6
    TUPLE_SIZE_BODY: int = 8
    TF_MASK: int = 2 ** 16 - 1  # Masking the 16 low bits of an integer
    client: storage.Client
    bucket: storage.Bucket

    def __init__(self, bucket_name: str) -> None:
        self.client = storage.Client()
        self.bucket = self.client.get_bucket(bucket_name)

    def download_from_buck(self, source: str, dest: str) -> None:
        blob = self.bucket.get_blob(source)
        blob.download_to_filename(dest)

    def get_pickle_file(self, source: str, dest: str) -> Any:
        if dest not in os.listdir("."):
            self.download_from_buck(source, dest)
        with open(dest, "rb") as f:
            return pkl.load(f)

    def get_inverted_index(self, source_idx: str, dest_file: str) -> InvertedIndex:
        self.download_from_buck(source_idx, dest_file)
        return InvertedIndex().read_index(".", dest_file.split(".")[0])

    def read_posting_list(
            self, inverted: InvertedIndex, w: str, index_name: str, isBody: bool = False, is_production: bool = False
    ) -> List[Tuple[int, Union[int, float]]]:
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
                            continue
                else:
                    pass
