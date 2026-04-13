{% extends "base.html" %}
{% block content %}
<div class="text-center py-5">
  <i class="bi bi-search text-secondary" style="font-size:4rem;"></i>
  <h1 class="display-4 fw-bold text-primary mt-3">404</h1>
  <p class="text-muted">Page not found.</p>
  <a href="{{ url_for('dashboard.index') }}" class="btn btn-primary mt-2">
    <i class="bi bi-house-fill me-1"></i>Go to Dashboard
  </a>
</div>
{% endblock %}
