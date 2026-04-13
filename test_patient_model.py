{% extends "base.html" %}
{% block extra_head %}
<script src="https://cdn.jsdelivr.net/npm/chart.js@4.4.2/dist/chart.umd.min.js"></script>
{% endblock %}

{% block content %}

<!-- Stat Cards -->
<div class="row g-3 mb-4">
  <div class="col-6 col-xl-3">
    <div class="stat-card" style="background:linear-gradient(135deg,#1a3c5e,#2e86de);">
      <div>
        <div class="stat-num">{{ stats.total }}</div>
        <div class="stat-label">Total Patients</div>
      </div>
      <i class="bi bi-people-fill stat-icon"></i>
    </div>
  </div>
  <div class="col-6 col-xl-3">
    <div class="stat-card" style="background:linear-gradient(135deg,#922b21,#e74c3c);">
      <div>
        <div class="stat-num">{{ stats.stroke_count }}</div>
        <div class="stat-label">Stroke Cases &nbsp;<strong>{{ stats.stroke_pct }}%</strong></div>
      </div>
      <i class="bi bi-activity stat-icon"></i>
    </div>
  </div>
  <div class="col-6 col-xl-3">
    <div class="stat-card" style="background:linear-gradient(135deg,#784212,#e67e22);">
      <div>
        <div class="stat-num">{{ stats.hypertension_count }}</div>
        <div class="stat-label">Hypertension Cases</div>
      </div>
      <i class="bi bi-heart-pulse stat-icon"></i>
    </div>
  </div>
  <div class="col-6 col-xl-3">
    <div class="stat-card" style="background:linear-gradient(135deg,#0e6655,#27ae60);">
      <div>
        <div class="stat-num">{{ stats.avg_age }}</div>
        <div class="stat-label">Average Patient Age</div>
      </div>
      <i class="bi bi-person-badge stat-icon"></i>
    </div>
  </div>
</div>

<!-- Secondary Stats -->
<div class="row g-3 mb-4">
  <div class="col-sm-4">
    <div class="card p-3 text-center">
      <div class="text-muted small mb-1"><i class="bi bi-droplet-fill text-danger me-1"></i>Heart Disease Cases</div>
      <div class="fw-bold fs-4">{{ stats.heart_disease_count }}</div>
    </div>
  </div>
  <div class="col-sm-4">
    <div class="card p-3 text-center">
      <div class="text-muted small mb-1"><i class="bi bi-speedometer text-warning me-1"></i>Avg Glucose (mg/dL)</div>
      <div class="fw-bold fs-4">{{ stats.avg_glucose }}</div>
    </div>
  </div>
  <div class="col-sm-4">
    <div class="card p-3 text-center">
      <div class="text-muted small mb-1"><i class="bi bi-clipboard2-pulse text-info me-1"></i>Average BMI</div>
      <div class="fw-bold fs-4">{{ stats.avg_bmi }}</div>
    </div>
  </div>
</div>

<!-- Charts -->
<div class="row g-3 mb-4">
  <div class="col-md-4">
    <div class="card h-100">
      <div class="card-header bg-white border-0 pb-0 pt-3">
        <h6 class="fw-bold text-primary mb-0 small text-uppercase">
          <i class="bi bi-pie-chart-fill me-1"></i>Stroke Distribution
        </h6>
      </div>
      <div class="card-body d-flex align-items-center justify-content-center" style="max-height:220px;">
        <canvas id="strokeChart"></canvas>
      </div>
    </div>
  </div>
  <div class="col-md-4">
    <div class="card h-100">
      <div class="card-header bg-white border-0 pb-0 pt-3">
        <h6 class="fw-bold text-primary mb-0 small text-uppercase">
          <i class="bi bi-gender-ambiguous me-1"></i>Gender Breakdown
        </h6>
      </div>
      <div class="card-body d-flex align-items-center justify-content-center" style="max-height:220px;">
        <canvas id="genderChart"></canvas>
      </div>
    </div>
  </div>
  <div class="col-md-4">
    <div class="card h-100">
      <div class="card-header bg-white border-0 pb-0 pt-3">
        <h6 class="fw-bold text-primary mb-0 small text-uppercase">
          <i class="bi bi-bar-chart-fill me-1"></i>Smoking Status
        </h6>
      </div>
      <div class="card-body" style="max-height:220px;">
        <canvas id="smokeChart"></canvas>
      </div>
    </div>
  </div>
</div>

<!-- Quick Actions -->
<div class="row g-3">
  <div class="col-sm-6 col-md-3">
    <a href="{{ url_for('patients.list_patients') }}" class="text-decoration-none">
      <div class="card p-3 text-center h-100">
        <i class="bi bi-table text-primary fs-2"></i>
        <div class="fw-semibold mt-2 small">View All Patients</div>
      </div>
    </a>
  </div>
  <div class="col-sm-6 col-md-3">
    <a href="{{ url_for('patients.add_patient') }}" class="text-decoration-none">
      <div class="card p-3 text-center h-100">
        <i class="bi bi-person-plus-fill text-success fs-2"></i>
        <div class="fw-semibold mt-2 small">Add New Patient</div>
      </div>
    </a>
  </div>
  <div class="col-sm-6 col-md-3">
    <a href="{{ url_for('patients.list_patients') }}?stroke=1" class="text-decoration-none">
      <div class="card p-3 text-center h-100">
        <i class="bi bi-exclamation-triangle-fill text-danger fs-2"></i>
        <div class="fw-semibold mt-2 small">Stroke Cases Only</div>
      </div>
    </a>
  </div>
  <div class="col-sm-6 col-md-3">
    <div class="card p-3 text-center h-100">
      <i class="bi bi-shield-lock-fill text-warning fs-2"></i>
      <div class="fw-semibold mt-2 small">Security Active</div>
      <div class="text-muted" style="font-size:.72rem;">CSRF · Hashing · Sessions</div>
    </div>
  </div>
</div>

{% endblock %}

{% block extra_scripts %}
<script>
const strokeCount = {{ stats.stroke_count }};
const noStroke    = {{ stats.total - stats.stroke_count }};
const genderData  = {{ stats.gender_counts | tojson }};
const smokingData = {{ stats.smoking_counts | tojson }};

new Chart(document.getElementById('strokeChart'), {
  type: 'doughnut',
  data: {
    labels: ['No Stroke', 'Had Stroke'],
    datasets: [{ data: [noStroke, strokeCount],
      backgroundColor: ['#27ae60','#e74c3c'], borderWidth: 2 }]
  },
  options: { responsive:true, maintainAspectRatio:true,
    plugins: { legend:{ position:'bottom', labels:{ font:{ size:11 } } } } }
});

new Chart(document.getElementById('genderChart'), {
  type: 'pie',
  data: {
    labels: Object.keys(genderData),
    datasets: [{ data: Object.values(genderData),
      backgroundColor: ['#2e86de','#e91e8c','#8e44ad'], borderWidth: 2 }]
  },
  options: { responsive:true, maintainAspectRatio:true,
    plugins: { legend:{ position:'bottom', labels:{ font:{ size:11 } } } } }
});

new Chart(document.getElementById('smokeChart'), {
  type: 'bar',
  data: {
    labels: Object.keys(smokingData).map(k => k.charAt(0).toUpperCase()+k.slice(1)),
    datasets: [{ label: 'Patients', data: Object.values(smokingData),
      backgroundColor: ['#1abc9c','#3498db','#e74c3c','#95a5a6'], borderRadius: 5 }]
  },
  options: { responsive:true, indexAxis:'y',
    plugins:{ legend:{ display:false } },
    scales:{ x:{ beginAtZero:true } } }
});
</script>
{% endblock %}
