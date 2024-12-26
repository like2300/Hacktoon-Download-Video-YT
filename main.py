import os
import flet as ft
import subprocess
from threading import Thread
import nest_asyncio

# Fonction pour télécharger la vidéo ou l'audio
def telecharger_media(url, dossier, progress_bar, page, type_media="video", qualite="best"):
    """Télécharge une vidéo ou un audio avec yt-dlp et met à jour la barre de progression."""
    progress_bar.value = 0
    page.update()

    # Définir la commande en fonction du type (vidéo ou audio)
    if type_media == "video":
        commande = [
            "yt-dlp",
            "-f", qualite,
            "-o", f"{dossier}/%(title)s.%(ext)s",
            url,
        ]
    else:
        commande = [
            "yt-dlp",
            "-f", "bestaudio",
            "-o", f"{dossier}/%(title)s.%(ext)s",
            url,
        ]

    try:
        process = subprocess.Popen(
            commande, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True
        )
        for line in process.stdout:
            if "Downloading" in line:
                progress_bar.value += 0.1  # Simule une progression
                page.update()

        process.wait()
        progress_bar.value = 1
        page.snack_bar = ft.SnackBar(ft.Text("Téléchargement terminé !"), open=True)
        page.update()

    except Exception as e:
        page.snack_bar = ft.SnackBar(ft.Text(f"Erreur : {e}"), open=True)
        page.update()

# Fonction pour créer l'interface
def creer_interface(page: ft.Page):
    page.title = "Hacktoon Download Video YT"
    page.window_width = 800
    page.window_height = 600
    page.theme_mode = ft.ThemeMode.LIGHT

    # Dossier de téléchargement
    dossier_telechargement = os.path.expanduser("~/Téléchargements")
    if not os.path.exists(dossier_telechargement):
        os.makedirs(dossier_telechargement)

    # Onglets
    onglets = ft.Tabs(
        selected_index=0,
        tabs=[
            ft.Tab(text="Télécharger Vidéo"),
            ft.Tab(text="Télécharger Audio"),
            ft.Tab(text="Vidéos téléchargées"),
        ],
    )

    # Onglet Téléchargement Vidéo
    url_input_video = ft.TextField(label="Entrez l'URL de la vidéo", expand=True)
    progress_bar_video = ft.ProgressBar(width=500, value=0)
    qualite_video = ft.Dropdown(
        options=[
            ft.dropdown.Option("best"),
            ft.dropdown.Option("worst"),
            ft.dropdown.Option("720p"),
            ft.dropdown.Option("1080p"),
        ],
        label="Qualité de la vidéo",
        value="best"
    )
    bouton_telecharger_video = ft.ElevatedButton(
        "Télécharger Vidéo",
        on_click=lambda _: Thread(
            target=telecharger_media,
            args=(url_input_video.value, dossier_telechargement, progress_bar_video, page, "video", qualite_video.value),
        ).start(),
    )

    onglet_telecharger_video = ft.Column(
        [
            ft.Text("Téléchargeur de vidéos", style=ft.TextThemeStyle.HEADLINE_SMALL),
            url_input_video,
            qualite_video,
            bouton_telecharger_video,
            progress_bar_video,
        ],
        alignment=ft.MainAxisAlignment.CENTER,
        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
    )

    # Onglet Téléchargement Audio
    url_input_audio = ft.TextField(label="Entrez l'URL de l'audio", expand=True)
    progress_bar_audio = ft.ProgressBar(width=500, value=0)
    qualite_audio = ft.Dropdown(
        options=[
            ft.dropdown.Option("best"),
            ft.dropdown.Option("worst"),
        ],
        label="Qualité de l'audio",
        value="best"
    )
    bouton_telecharger_audio = ft.ElevatedButton(
        "Télécharger Audio",
        on_click=lambda _: Thread(
            target=telecharger_media,
            args=(url_input_audio.value, dossier_telechargement, progress_bar_audio, page, "audio", qualite_audio.value),
        ).start(),
    )

    onglet_telecharger_audio = ft.Column(
        [
            ft.Text("Téléchargeur d'audio", style=ft.TextThemeStyle.HEADLINE_SMALL),
            url_input_audio,
            qualite_audio,
            bouton_telecharger_audio,
            progress_bar_audio,
        ],
        alignment=ft.MainAxisAlignment.CENTER,
        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
    )

    # Onglet Vidéos téléchargées
    def rafraichir_liste_videos():
        fichiers = os.listdir(dossier_telechargement)
        liste_videos.controls.clear()
        for fichier in fichiers:
            liste_videos.controls.append(ft.Text(fichier))
        page.update()

    liste_videos = ft.Column()
    bouton_rafraichir = ft.ElevatedButton(
        "Rafraîchir la liste", on_click=lambda _: rafraichir_liste_videos()
    )
    bouton_ouvrir_dossier = ft.ElevatedButton(
        "Ouvrir le dossier", on_click=lambda _: subprocess.run(["open", dossier_telechargement])
    )

    onglet_videos = ft.Column(
        [
            ft.Text("Vidéos téléchargées", style=ft.TextThemeStyle.HEADLINE_SMALL),
            bouton_rafraichir,
            liste_videos,
            bouton_ouvrir_dossier,
        ],
        alignment=ft.MainAxisAlignment.START,
        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
    )

    # Contenu principal des onglets
    contenu = ft.Stack(
        [
            ft.Container(onglet_telecharger_video, visible=onglets.selected_index == 0),
            ft.Container(onglet_telecharger_audio, visible=onglets.selected_index == 1),
            ft.Container(onglet_videos, visible=onglets.selected_index == 2),
        ]
    )

    def changer_onglet(e):
        contenu.controls[0].visible = onglets.selected_index == 0
        contenu.controls[1].visible = onglets.selected_index == 1
        contenu.controls[2].visible = onglets.selected_index == 2
        page.update()

    onglets.on_change = changer_onglet

    # Interface principale
    page.add(
        ft.Column(
            [
                onglets,
                contenu,
            ],
            expand=True,
        )
    )

# Appliquer nest_asyncio pour les boucles d'événements
nest_asyncio.apply()

# Lancer l'application Flet
if __name__ == "__main__":
    ft.app(target=creer_interface)
