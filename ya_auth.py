import ctypes
import json
import subprocess
import uuid
import winreg

import requests


class ApiClient:
    BASE_URL = "https://p01--script-serve--5yyh9pxyhqq4.code.run"

    def _api(self, method: str, endpoint: str, data: dict = None, token: str = None) -> dict | None:
        url = f"{self.BASE_URL}{endpoint}"
        headers = {}
        if token:
            headers["Authorization"] = f"Bearer {token}"
        try:
            resp = requests.request(method, url, json=data, headers=headers, timeout=10)
            resp.raise_for_status()
            return resp.json()
        except Exception:
            return None

    def login(self, username: str, password: str, device_mac: str) -> dict | None:
        return self._api("POST", "/api/login", {"username": username, "password": password, "device_mac": device_mac})

    def register_free(self, username: str, password: str, device_mac: str) -> dict | None:
        return self._api("POST", "/api/register-free", {"username": username, "password": password, "device_mac": device_mac})

    def activate(self, username: str, password: str, invite_code: str, device_mac: str) -> dict | None:
        return self._api("POST", "/api/activate", {"username": username, "password": password, "invite_code": invite_code, "device_mac": device_mac})

    def change_password(self, username: str, old_password: str, new_password: str) -> dict | None:
        return self._api("POST", "/api/change-password", {"username": username, "old_password": old_password, "new_password": new_password})

    def check_version(self) -> dict | None:
        return self._api("GET", "/api/version")


class CredentialStore:
    REGISTRY_PATH = r"Software\MHSG"

    def _dpapi_encrypt(self, data: bytes) -> bytes:
        class DATA_BLOB(ctypes.Structure):
            _fields_ = [("cbData", ctypes.c_ulong), ("pbData", ctypes.POINTER(ctypes.c_char))]
        blob_in = DATA_BLOB(len(data), ctypes.create_string_buffer(data, len(data)))
        blob_out = DATA_BLOB()
        if ctypes.windll.crypt32.CryptProtectData(ctypes.byref(blob_in), None, None, None, None, 0, ctypes.byref(blob_out)):
            buf = ctypes.string_at(blob_out.pbData, blob_out.cbData)
            ctypes.windll.kernel32.LocalFree(blob_out.pbData)
            return buf
        raise OSError("DPAPI加密失败")

    def _dpapi_decrypt(self, data: bytes) -> bytes:
        class DATA_BLOB(ctypes.Structure):
            _fields_ = [("cbData", ctypes.c_ulong), ("pbData", ctypes.POINTER(ctypes.c_char))]
        blob_in = DATA_BLOB(len(data), ctypes.create_string_buffer(data, len(data)))
        blob_out = DATA_BLOB()
        if ctypes.windll.crypt32.CryptUnprotectData(ctypes.byref(blob_in), None, None, None, None, 0, ctypes.byref(blob_out)):
            buf = ctypes.string_at(blob_out.pbData, blob_out.cbData)
            ctypes.windll.kernel32.LocalFree(blob_out.pbData)
            return buf
        raise OSError("DPAPI解密失败")

    def save(self, username: str, password: str, auto_login: bool = True) -> None:
        payload = json.dumps({"u": username, "p": password, "a": auto_login}).encode()
        encrypted = self._dpapi_encrypt(payload)
        key = winreg.CreateKey(winreg.HKEY_CURRENT_USER, self.REGISTRY_PATH)
        try:
            winreg.SetValueEx(key, "cred", 0, winreg.REG_BINARY, encrypted)
        finally:
            winreg.CloseKey(key)

    def load(self) -> tuple[str | None, str | None, bool]:
        try:
            key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, self.REGISTRY_PATH)
            try:
                encrypted, _ = winreg.QueryValueEx(key, "cred")
            finally:
                winreg.CloseKey(key)
            decrypted = self._dpapi_decrypt(encrypted)
            data = json.loads(decrypted)
            return data["u"], data["p"], data.get("a", False)
        except Exception:
            return None, None, False

    def clear(self) -> None:
        try:
            winreg.DeleteKey(winreg.HKEY_CURRENT_USER, self.REGISTRY_PATH)
        except OSError:
            pass


def get_mac_address() -> str:
    mac = uuid.getnode()
    return "-".join(f"{(mac >> (8 * i)) & 0xFF:02X}" for i in range(5, -1, -1))


def is_virtual_machine() -> bool:
    vm_keywords = {"vmware", "virtualbox", "kvm", "qemu", "xen", "bochs", "hyper-v"}
    try:
        result = subprocess.run(
            ["powershell", "-Command", "Get-CimInstance Win32_ComputerSystem | Select-Object Manufacturer,Model | ConvertTo-Json"],
            capture_output=True, text=True, timeout=10,
        )
        info = result.stdout.lower()
        return any(kw in info for kw in vm_keywords)
    except Exception:
        return False
