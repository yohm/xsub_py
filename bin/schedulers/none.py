import pathlib,io,os,subprocess
from typing import List,Tuple,Dict

class NoneScheduler:

  PARAMETERS = {
    "mpi_procs":   { "description": "MPI process", "default": 1, "format": r'^[1-9]\d*$'},
    "omp_threads": { "description": "OMP threads", "default": 1, "format": r'^[1-9]\d*$'}
  }

  @staticmethod
  def validate_parameters(params: dict) -> None:
    # check if the given parameters are valid
    # if not valid, raise an Exception
    pass

  @staticmethod
  def parent_script(parametes: dict, job_file: pathlib.Path, work_dir: pathlib.Path) -> str:
    return f". {job_file}\n"

  @staticmethod
  def submit_job(script_path: pathlib.Path, work_dir: pathlib.Path, log_dir: pathlib.Path, log: io.TextIOBase, parameters: dict) -> Tuple[str,str]:
    cmd = f"nohup bash {script_path.absolute()} > /dev/null 2>&1 < /dev/null & echo $!"
    log.write(f"{cmd} is invoked\n")
    output = ""
    os.makedirs(work_dir, exist_ok=True)
    result = subprocess.run(cmd, shell=True, cwd=work_dir, check=True, stdout=subprocess.PIPE)
    psid = str(int(result.stdout.splitlines()[-1]))
    log.write(f"process id: {psid}\n")
    return (psid, result.stdout.decode())

  @staticmethod
  def all_status() -> str:
    cmd = "ps uxr | head -n 10"
    result = subprocess.run(cmd, shell=True, check=False, stdout=subprocess.PIPE)
    return result.stdout.decode()

  @staticmethod
  def multiple_status(job_ids: List[str]) -> Dict[str,Tuple[str,str]]:
    results = {}
    for job_id in job_ids:
      results[job_id] = NoneScheduler._status(job_id)
    return results

  @staticmethod
  def _status(job_id: str) -> Tuple[str,str]:
    cmd = f"ps -p {job_id}"
    result = subprocess.run(cmd, shell=True, check=False, stdout=subprocess.PIPE)
    status = "running" if result.returncode == 0 else "finished"
    return (status, result.stdout.decode())

  @staticmethod
  def delete(job_id: str) -> str:
    cmd = f"ps -p {job_id} -o 'pgid'"   # get process group id of {job_id}
    result = subprocess.run(cmd, check=False, shell=True, stdout=subprocess.PIPE)
    if result.returncode != 0:
      return f"process for {job_id} is not found"
    pgid = int(result.stdout.decode().splitlines()[-1])  # process group id
    cmd = f"kill -TERM -{pgid}"
    subprocess.run(cmd, shell=True, check=True)
    return f"process group {pgid} is successfully terminated"