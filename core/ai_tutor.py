import requests
from cryptography.fernet import Fernet
import os
import hashlib
import base64
try:
    import winreg
except Exception:
    winreg = None

class AITutor:
    def __init__(self, config_path):
        self.api_key = self._load_api_key(config_path)
        self.url = "https://api.anthropic.com/v1/messages"

    @staticmethod
    def is_configured(config_path):
        return os.path.exists(config_path)

    def _load_api_key(self, path):
        with open(path, "rb") as f:
            encrypted = f.read()
        key = self._get_machine_key()
        fernet = Fernet(key)
        return fernet.decrypt(encrypted).decode()

    def _get_machine_key(self):
        machine_id = None
        try:
            if winreg:
                key = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\Microsoft\Cryptography")
                machine_id, _ = winreg.QueryValueEx(key, "MachineGuid")
        except Exception:
            machine_id = None
        if not machine_id:
            machine_id = os.environ.get('ENGLISHCOACH_MACHINE_ID') or (os.uname().nodename if hasattr(os, 'uname') else os.environ.get('COMPUTERNAME', 'unknown'))
        digest = hashlib.sha256(machine_id.encode('utf-8')).digest()
        return base64.urlsafe_b64encode(digest)

    def get_writing_feedback(self, essay, task_type, exam_type):
        exam_label = exam_type
        if hasattr(exam_type, 'name'):
            exam_label = exam_type.name
        prompt = f"""You are an expert {exam_label} examiner. Evaluate this {task_type} response.
        Provide: (1) Band score estimate, (2) Task Achievement, (3) Coherence,
        (4) Lexical Resource with word upgrades, (5) Grammar Range with 3 corrections,
        (6) One complete rewrite of the weakest paragraph.
        Essay: {essay}"""
        response = requests.post(
            self.url,
            headers={
                "x-api-key": self.api_key,
                "Content-Type": "application/json",
                "anthropic-version": "2023-06-01",
            },
            json={
                "model": "claude-sonnet-4-6",
                "max_tokens": 1024,
                "messages": [{"role": "user", "content": prompt}],
            },
            timeout=60,
        )
        response.raise_for_status()
        data = response.json()
        return data.get("content", [{}])[0].get("text", "")