from ttkbootstrap import Window

from app.main_obs_ui import OBSTimerApp


def main():
    root = Window(themename="darkly")
    app = OBSTimerApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()
