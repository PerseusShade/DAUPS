import subprocess
import sys

def run_command(command):
    """Exécute une commande shell et gère les erreurs et les encodages."""
    try:
        print(f"Exécution de : {' '.join(command)}")
        result = subprocess.run(
            command,
            check=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            encoding='utf-8',
            errors='replace'
        )
        print(result.stdout)
        if result.stderr:
            print("Messages d'erreur (stderr) :\n", result.stderr, file=sys.stderr)
    except subprocess.CalledProcessError as e:
        print(f"La commande a échoué avec le code {e.returncode}.", file=sys.stderr)
        stderr = e.stderr.decode('utf-8', errors='replace') if isinstance(e.stderr, bytes) else e.stderr
        print(stderr, file=sys.stderr)
        sys.exit(e.returncode)

def main():
    commands = [
        ["node", "docs/generate-site.cjs"],
        ["node", "docs/generate-pdf.mjs"],
    ]

    for cmd in commands:
        run_command(cmd)

    print("Tous les scripts ont été exécutés avec succès.")

if __name__ == "__main__":
    main()