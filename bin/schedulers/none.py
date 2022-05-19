import pathlib,io,os,subprocess

class NoneScheduler:

  TEMPLATE = '''\
. {_job_file}
'''

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
  def submit_job(script_path: pathlib.Path, work_dir: pathlib.Path, log_dir: pathlib.Path, log: io.TextIOBase, parameters: dict) -> dict:
    cmd = f"nohup bash {script_path.absolute()} > /dev/null 2>&1 < /dev/null & echo $!"
    log.write(f"{cmd} is invoked\n")
    output = ""
    os.makedirs(work_dir, exist_ok=True)
    result = subprocess.run(cmd, shell=True, cwd=work_dir, check=True, capture_output=True)
    psid = str(int(result.stdout.splitlines()[-1]))
    log.write(f"process id: {psid}\n")
    return {"job_id": psid, "raw_output": [line.rstrip() for line in result.stdout.decode().splitlines()]}

  @staticmethod
  def all_status() -> str:
    cmd = "ps uxr | head -n 10"
    result = subprocess.run(cmd, shell=True, check=False, capture_output=True)
    return result.stdout.decode()

  @staticmethod
  def multiple_status(job_ids: list[str]) -> dict[str,dict]:
    results = {}
    for job_id in job_ids:
      results[job_id] = NoneScheduler._status(job_id)
    return results

  @staticmethod
  def _status(job_id: str):
    cmd = f"ps -p {job_id}"
    result = subprocess.run(cmd, shell=True, check=False, capture_output=True)
    status = "running" if result.returncode == 0 else "finished"
    return { "status": status, "raw_output": [line.rstrip() for line in result.stdout.decode().splitlines()] }