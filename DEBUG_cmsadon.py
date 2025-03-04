from app import app, db
from models.cmsaddon import CMSAddon
import logging
from datetime import datetime

# 📌 Configura il logging
logging.basicConfig(level=logging.INFO)

with app.app_context():
    try:
        # ✅ Dati degli addon da inserire
        addons = [
            (1, 'Norman', "Theme designed on simplicity, from the Latin derives from 'Normal' so a theme that expresses normality", 0.00, 'theme', '2024-11-04 19:04:13', '2024-11-04 19:04:47'),
            (2, 'Motion', 'Motion is a theme distributed free, developed to excite, as it does? by using a dynamic kit and fresh to the eye', 14.90, 'theme', '2024-11-04 19:09:24', '2024-11-04 19:59:45'),
            (3, 'Crabizk', 'Crabizk is a theme created by webdesigners and front-end developers, the conversion rate is much higher than other stores', 19.90, 'theme', '2024-11-04 19:11:51', '2024-11-04 19:59:41'),
            (4, 'Norman', 'Kit ui taken from the norman theme, there are all unique blocks of the theme.', 0.00, 'theme_ui', '2024-11-04 19:18:01', '2024-11-04 19:19:04'),
            (5, 'Motion', 'Kit ui taken from the theme Motion, there are all unique blocks of the theme.', 0.00, 'theme_ui', '2024-11-04 19:23:34', '2024-11-04 19:23:34'),
            (6, 'Userless', 'Kit ui taken from the theme Userless, there are all unique blocks of the theme.', 0.00, 'theme_ui', '2024-11-04 19:55:10', '2024-11-04 19:55:10'),
            (7, 'Userless', 'Userless is a soft theme and created by the usucapion of people’s passion ', 14.90, 'theme', '2024-11-04 19:56:42', '2024-11-04 19:56:42'),
            (8, 'Crabizk', 'Kit ui taken from the Crabizk theme, there are all unique blocks of the theme.', 7.90, 'theme_ui', '2024-11-04 20:01:04', '2024-11-04 20:01:04'),
            (9, 'No Plugin', "There is no plugin installed in your website, if you selected this options you can't use any plugin.", 0.00, 'plugin', '2024-11-05 01:01:33', '2024-11-13 15:03:29'),
            (10, 'Security Standard', 'This package contains the standard security for your store, such as SSL certificate and anti-virus.', 0.00, 'service', '2024-11-05 01:01:33', '2024-11-13 14:59:15'),
            (11, 'Security Pro', 'This package contains advanced (recommended) security for your site, such as SSL, DDoS attack protection, antivirus and malware scanning', 15.00, 'service', '2024-11-05 01:01:33', '2024-11-13 14:59:15'),
        ]

        # ✅ Inserimento dati nel database
        for addon in addons:
            new_addon = CMSAddon(
                id=addon[0],
                name=addon[1],
                description=addon[2],
                price=addon[3],
                addon_type=addon[4],
                created_at=datetime.strptime(addon[5], '%Y-%m-%d %H:%M:%S'),
                updated_at=datetime.strptime(addon[6], '%Y-%m-%d %H:%M:%S')
            )
            db.session.add(new_addon)

        db.session.commit()
        logging.info("✅ Dati inseriti correttamente nella tabella cms_addons.")

    except Exception as e:
        db.session.rollback()
        logging.error(f"❌ Errore durante l'inserimento dei dati: {str(e)}")