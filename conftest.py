<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <meta http-equiv="X-Content-Type-Options" content="nosniff">
  <meta http-equiv="X-Frame-Options" content="SAMEORIGIN">
  <title>{% block title %}{{ title }} — StrokeGuard{% endblock %}</title>

  <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.3/dist/css/bootstrap.min.css" rel="stylesheet">
  <link href="https://cdn.jsdelivr.net/npm/bootstrap-icons@1.11.3/font/bootstrap-icons.css" rel="stylesheet">

  <style>
    :root {
      --primary: #1a3c5e;
      --accent:  #2e86de;
      --sw: 240px;
    }
    body { background:#f4f7fb; font-family:'Segoe UI',system-ui,sans-serif; }

    /* Sidebar */
    #sidebar {
      width:var(--sw); min-height:100vh; background:var(--primary);
      position:fixed; top:0; left:0; display:flex; flex-direction:column; z-index:1000;
    }
    #sidebar .brand {
      padding:1.1rem 1rem; border-bottom:1px solid rgba(255,255,255,.1);
      color:#fff; font-size:1.1rem; font-weight:700;
    }
    #sidebar .brand span { color:#5dade2; }
    #sidebar .nav-link {
      color:rgba(255,255,255,.75); padding:.6rem 1.1rem; border-radius:6px;
      margin:2px 8px; display:flex; align-items:center; gap:.55rem;
      font-size:.92rem; transition:background .15s;
    }
    #sidebar .nav-link:hover,
    #sidebar .nav-link.active { background:rgba(255,255,255,.13); color:#fff; }

    /* Main */
    #main { margin-left:var(--sw); min-height:100vh; }
    .topbar {
      background:#fff; border-bottom:1px solid #e2e8f0;
      padding:.7rem 1.4rem; display:flex; align-items:center;
      justify-content:space-between; position:sticky; top:0; z-index:900;
      box-shadow:0 1px 4px rgba(0,0,0,.06);
    }
    .topbar .ptitle { font-weight:600; color:var(--primary); }

    /* Cards */
    .card { border:none; border-radius:12px; box-shadow:0 2px 8px rgba(0,0,0,.07); }

    /* Stat cards */
    .stat-card {
      border-radius:12px; padding:1.2rem 1.4rem; color:#fff;
      display:flex; justify-content:space-between; align-items:flex-start;
    }
    .stat-num   { font-size:1.9rem; font-weight:700; line-height:1; }
    .stat-label { font-size:.8rem; opacity:.85; margin-top:.2rem; }
    .stat-icon  { font-size:1.9rem; opacity:.75; }

    /* Table */
    .table thead th { background:var(--primary); color:#fff; font-weight:500; font-size:.87rem; }
    .table tbody tr:hover { background:#eaf2fb; }

    /* Badges */
    .b-stroke { background:#fde8e8; color:#c0392b; font-size:.78rem; }
    .b-ok     { background:#e8f8ee; color:#1e8449; font-size:.78rem; }

    /* Mobile */
    @media(max-width:767px){
      #sidebar{transform:translateX(-100%);}
      #sidebar.show{transform:translateX(0);}
      #main{margin-left:0;}
    }
  </style>
  {% block extra_head %}{% endblock %}
</head>
<body>

{% if current_user.is_authenticated %}
<!-- ── Sidebar ──────────────────────────────────────────────── -->
<nav id="sidebar">
  <div class="brand"><i class="bi bi-heart-pulse-fill me-1"></i>Stroke<span>Guard</span></div>
  <ul class="nav flex-column mt-1 flex-grow-1">
    <li><a class="nav-link {% if request.endpoint=='dashboard.index' %}active{% endif %}"
           href="{{ url_for('dashboard.index') }}">
      <i class="bi bi-speedometer2"></i> Dashboard</a></li>
    <li><a class="nav-link {% if request.blueprint=='patients' %}active{% endif %}"
           href="{{ url_for('patients.list_patients') }}">
      <i class="bi bi-people-fill"></i> All Patients</a></li>
    <li><a class="nav-link" href="{{ url_for('patients.add_patient') }}">
      <i class="bi bi-person-plus-fill"></i> Add Patient</a></li>
  </ul>
  <div class="px-3 py-3 border-top" style="border-color:rgba(255,255,255,.1)!important;">
    <small class="text-white-50 d-block">
      <i class="bi bi-person-circle me-1"></i>{{ current_user.username }}
      <span class="badge bg-secondary ms-1" style="font-size:.7rem;">{{ current_user.role }}</span>
    </small>
    <a href="{{ url_for('auth.logout') }}" class="btn btn-sm btn-outline-light w-100 mt-2">
      <i class="bi bi-box-arrow-right me-1"></i>Sign Out
    </a>
  </div>
</nav>

<!-- ── Main ────────────────────────────────────────────────── -->
<div id="main">
  <div class="topbar">
    <span class="ptitle">
      <button class="btn btn-sm btn-light me-2 d-md-none" id="sbToggle">
        <i class="bi bi-list"></i>
      </button>
      {% block page_title %}{{ title }}{% endblock %}
    </span>
    <span class="text-muted" style="font-size:.82rem;">
      <i class="bi bi-hospital-fill me-1 text-primary"></i>StrokeGuard &mdash; Secure Patient Management
    </span>
  </div>

  <div class="container-fluid p-4">
    {% with messages = get_flashed_messages(with_categories=true) %}
      {% for cat, msg in messages %}
        <div class="alert alert-{{ cat }} alert-dismissible fade show py-2" role="alert">
          {{ msg }}<button type="button" class="btn-close" data-bs-dismiss="alert"></button>
        </div>
      {% endfor %}
    {% endwith %}
{% else %}
<!-- Unauthenticated layout -->
<div class="min-vh-100 d-flex align-items-center justify-content-center"
     style="background:linear-gradient(135deg,#1a3c5e 0%,#2e86de 100%);">
  <div class="container" style="max-width:430px;">
    <div class="text-center mb-3">
      <i class="bi bi-heart-pulse-fill text-white" style="font-size:2.8rem;"></i>
      <h1 class="text-white fw-bold mt-1">StrokeGuard</h1>
      <p class="text-white-50 small">Secure Patient Management System</p>
    </div>
    {% with messages = get_flashed_messages(with_categories=true) %}
      {% for cat, msg in messages %}
        <div class="alert alert-{{ cat }} py-2">{{ msg }}</div>
      {% endfor %}
    {% endwith %}
{% endif %}

    {% block content %}{% endblock %}

{% if current_user.is_authenticated %}
  </div>
</div>
{% else %}
  </div>
</div>
{% endif %}

<script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.3/dist/js/bootstrap.bundle.min.js"></script>
<script>
  const sb = document.getElementById("sidebar");
  const btn = document.getElementById("sbToggle");
  if(btn) btn.addEventListener("click", () => sb.classList.toggle("show"));
</script>
{% block extra_scripts %}{% endblock %}
</body>
</html>
