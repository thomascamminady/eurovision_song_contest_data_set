import os

if __name__ == "__main__":
    for year in range(2016, 2026):
        folder = f"data/{year}"
        if not os.path.exists(folder):
            os.makedirs(folder)
            if not os.path.exists(f"{folder}/public.html"):
                with open(f"{folder}/public.html", "w") as f:
                    f.write("")
            if not os.path.exists(f"{folder}/jury.html"):
                with open(f"{folder}/jury.html", "w") as f:
                    f.write("")
