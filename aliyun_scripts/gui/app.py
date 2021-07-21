import tkinter as tk

from aliyun_scripts.lib.actions import shutdown_ecs, start_ecs
from aliyun_scripts.lib.utils import get_client_config_and_ecs
from aliyun_scripts.tools.eip_tool import (
    load_config_and_unbind_allocate_and_bind_new_eip,
    release_eip,
    unbind_release,
)


class Application(tk.Frame):
    def __init__(self, master=None):
        super().__init__(master)
        self.master = master
        self.pack(ipadx=2, ipady=2, padx=20, pady=20)
        self.client, _, self.ecs = get_client_config_and_ecs()
        self.create_widgets()

    def create_widgets(self):
        self.btns = tk.Frame(self)
        self.btns.pack(side="top")

        self.status_btn = tk.Button(self.btns)
        self.status_btn["text"] = f"Refresh"
        self.status_btn["command"] = self.get_status
        self.status_btn.pack(side="left")

        self.status_btn = tk.Button(self.btns)
        self.status_btn["text"] = f"Start"
        self.status_btn["command"] = lambda: start_ecs(self.client, self.ecs)
        self.status_btn.pack(side="left")

        self.status_btn = tk.Button(self.btns)
        self.status_btn["text"] = f"Stop"
        self.status_btn["command"] = lambda: shutdown_ecs(
            self.client, self.ecs, "StopCharging"
        )
        self.status_btn.pack(side="left")

        self.status_btn = tk.Button(self.btns)
        self.status_btn["text"] = f"Rebind"
        self.status_btn[
            "command"
        ] = lambda: load_config_and_unbind_allocate_and_bind_new_eip(
            True, False, True, True
        )
        self.status_btn.pack(side="left")

        self.status_btn = tk.Button(self.btns)
        self.status_btn["text"] = f"Release"
        self.status_btn["command"] = lambda: unbind_release(
            self.client, self.ecs, True, True, False
        )
        self.status_btn.pack(side="left")

        self.status_text = tk.Label(self)
        self.update_text()
        self.status_text.pack(side="top")

        self.quit = tk.Button(self, text="QUIT", fg="red", command=self.master.destroy)

    def update_text(self):
        status = f"""
InstanceId: {self.ecs.InstanceId}
InstanceName: {self.ecs.InstanceName}
RegionId: {self.ecs.RegionId}
IP: {self.ecs.EipAddress.IpAddress if self.ecs.EipAddress is not None else "N/A"}
Status: {self.ecs.Status}
        """.strip()
        self.status_text["text"] = status

    def get_status(self):
        self.client, _, self.ecs = get_client_config_and_ecs()
        self.update_text()


def main():
    root = tk.Tk()
    app = Application(master=root)
    app.mainloop()


if __name__ == "__main__":
    main()
