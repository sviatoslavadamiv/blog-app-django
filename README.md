# Django Blog Project

A fully featured blog application built with Django and PostgreSQL.  
This project includes advanced search, tagging, feeds, sitemaps, Markdown support, and a PostgreSQL-backed recommendation system.

---

## 🚀 Features

- ✅ **Post Publishing System** — Create, edit, and publish blog posts
- 🏷️ **Tagging Support** — Organize posts using `django-taggit`
- 🔍 **Advanced Search** — Full-text + trigram similarity (PostgreSQL)
- 🤝 **Related Posts** — Display similar posts based on shared tags
- 💬 **Post Comments** — Readers can leave comments under posts
- 📩 **Share via Email** — Visitors can share posts by sending them via email
- 🌐 **SEO** — Canonical URLs, slugs, sitemap.xml, and meta-optimized structure
- 📰 **RSS/Atom Feeds** — Readers can subscribe to new posts
- 🧩 **Custom Template Tags & Filters to display latest posts and most commented posts and to render Markdown**
- 🐘 **PostgreSQL Integration** — Uses PostgreSQL for scalable querying
- 🎯 **PEP 8 Code Style** — Clean, consistent, and well-formatted

---

## 📦 Installation

Follow these steps to set up the project locally:

### 1. Clone the repository

```
git clone https://github.com/your-username/django-blog.git
cd django-blog
```

### 2. Create and activate a virtual environment

```
python3 -m venv .venv
source .venv/bin/activate # macOS/Linux

# For Windows:
.venv\Scripts\activate
```

### 3. Install dependencies

```
pip install --upgrade pip
pip install -r requirements.txt
```

### 4. Set up PostgreSQL

First, download and install Docker for your OS. After installing Docker on your machine, you can easily pull the PostgreSQL
Docker image. Run the following command from the shell:

```
docker pull postgres:16.2
```

Execute the following command in the shell to start the PostgreSQL Docker container:

```
docker run --name=blog_db -e POSRGRES_DB=blog -e POSTGRES_USER=blog -e POSTGRES_PASSWORD=xxxxx -p 5432:5432 -d postgres:16.2
```

Replace xxxxx with the desired password for your database user.

### 4. Edit .env.example in myblog folder

Fill in the required values in the `.env.example` file, then rename the file to `.env` by removing the `.example` extension.  

By default, the project is configured to use Gmail’s SMTP server for sending emails.
If you prefer to use a different email provider, update the email settings accordingly in the `.env` file and in `settings.py`.


### 5. Apply migrations

```
python manage.py migrate
```

### 6. Create a superuser (admin access)

```
python manage.py createsuperuser
```

### 7. Run the development server

```
python manage.py runserver
```

## ✅ You're ready to go!
Now you can:
- Create blog posts 
- Tag them 
- Search 
- Comment 
- Share posts via email 
- View RSS feed and sitemap

