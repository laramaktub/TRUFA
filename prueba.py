import os
import tempfile

cache_path="/gpfs/csic_users/lara/server_side/"
job_name="pruebayeye"
os.chdir(cache_path)

# Preparing temporary files for submission:
fd, cmd_path = tempfile.mkstemp(dir="tmp",prefix=job_name + "_")
job_file = os.path.basename(cmd_path)
print job_file
