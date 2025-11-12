import pandas as pd
import subprocess
from Bio import Blast
from Bio import SeqIO
from Bio.Blast.Applications import NcbimakeblastdbCommandline, NcbiblastpCommandline 
from Bio.Blast import NCBIXML

input_data = pd.read_csv("./dataset/final_testing.csv")
input_data["id"] = list(range(0,len(input_data))) #add id column


f= open("./outputs.csv","w") #create a file file to store outputs
f.write("seq,true,predicted\n") #write header
for i, row in input_data.iterrows():
    #get current sequence entry code, with the classification output
    true_class = row["output"]#real classification
    entry = row["id"]
    seq = row["Sequence"]
    #create a single query fasta
    q = open("./query.fasta","w")
    q.write(">test\n")
    q.write(f"{seq}\n") 
    q.close()

    #run a blast search
    blastp_cline = NcbiblastpCommandline(
        query="query.fasta", 
        db="my_protein_db", 
        evalue=0.001, 
        outfmt=5,  # XML format
        out="results.xml"
    )
    stdout, stderr = blastp_cline()
    if stderr:
        subprocess.run(["echo", f"error: {stderr}"])
    #Parse BLAST Results
    with open("results.xml") as result_handle:
        blast_record = NCBIXML.read(result_handle)

    # Step 5: Get Most Similar Sequence
    predicted_class = 0
    try:
        best_match = blast_record.alignments[0]  # Top hit
        predicted_class = str(best_match.title).split("-")[1]
        subprocess.run(["echo", f"predicted: {predicted_class}"])
        f.write(f"{seq},{true_class},{predicted_class}\n")#write rows to the csv
    except:
        subprocess.run(["echo", "No significant matches found."])
        f.write(f"{seq},{true_class},{predicted_class}\n")#write rows to the csv
        continue
f.close()