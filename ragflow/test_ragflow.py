import rag
import psutil
import os

process = psutil.Process(os.getpid())
memory_mb = process.memory_info().rss / 1024 / 1024
print(f"RAGFlow memory usage: {memory_mb:.1f} MB")

bengali_text = "???? ??????? ??? ?,??,??? ????"
print(f"Bengali text test: {bengali_text}")
print("RAGFlow system ready!")
