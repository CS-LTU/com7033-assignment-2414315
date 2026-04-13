{% extends "base.html" %}
{% block content %}
<div class="text-center py-5">
  <i class="bi bi-shield-lock-fill text-warning" style="font-size:4rem;"></i>
  <h1 class="display-4 fw-bold text-primary mt-3">403</h1>
  <p class="text-muted">You don't have permission to view this page.</p>
  <a href="{{ url_for('dashboard.index') }}" class="btn btn-primary mt-2">
    <i class="bi bi-house-fill me-1"></i>Go to Dashboard
  </a>
</div>
{% endblock %}
