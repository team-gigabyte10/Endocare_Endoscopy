/**
 * Endocare - Endoscopy Management System
 * Interactive UI Logic & Desktop Simulation Controls
 */

document.addEventListener('DOMContentLoaded', () => {
  initLiveClock();
  initDropdownDismiss();
});

/* ----------------- 1. LIVE SYSTEM CLOCK ----------------- */
function initLiveClock() {
  const dateEl = document.getElementById('clockDate');
  const timeEl = document.getElementById('clockTime');

  function update() {
    const now = new Date();
    const dateOptions = { weekday: 'short', month: 'short', day: 'numeric', year: 'numeric' };
    const timeOptions = { hour: '2-digit', minute: '2-digit', second: '2-digit', hour12: true };

    if (dateEl) dateEl.textContent = now.toLocaleDateString('en-US', dateOptions);
    if (timeEl) timeEl.textContent = now.toLocaleTimeString('en-US', timeOptions);
  }

  update();
  setInterval(update, 1000);
}

/* ----------------- 2. RESOLUTION SIMULATOR SWITCHER ----------------- */
function setResolution(mode) {
  const shell = document.getElementById('windowShell');
  const btn1920 = document.getElementById('btnRes1920');
  const btn1366 = document.getElementById('btnRes1366');
  const btnFluid = document.getElementById('btnResFluid');

  [btn1920, btn1366, btnFluid].forEach(b => b?.classList.remove('active'));
  shell.classList.remove('res-1920', 'res-1366', 'res-fluid');

  if (mode === '1366') {
    shell.classList.add('res-1366');
    btn1366?.classList.add('active');
  } else if (mode === 'fluid') {
    shell.classList.add('res-fluid');
    btnFluid?.classList.add('active');
  } else {
    shell.classList.add('res-1920');
    btn1920?.classList.add('active');
  }
}

/* ----------------- 3. CAPTURE CARD LIBRARY DROPDOWN ----------------- */
function toggleCaptureDropdown(event) {
  event.stopPropagation();
  const btn = document.getElementById('btnCaptureDropdown');
  const menu = document.getElementById('captureMenu');
  
  const isOpen = menu.classList.contains('show');
  if (isOpen) {
    menu.classList.remove('show');
    btn.classList.remove('open');
  } else {
    menu.classList.add('show');
    btn.classList.add('open');
  }
}

function initDropdownDismiss() {
  document.addEventListener('click', (e) => {
    const wrapper = document.getElementById('captureDropdownWrapper');
    const menu = document.getElementById('captureMenu');
    const btn = document.getElementById('btnCaptureDropdown');
    
    if (wrapper && !wrapper.contains(e.target)) {
      menu?.classList.remove('show');
      btn?.classList.remove('open');
    }
  });
}

/* ----------------- 4. MODAL MANAGEMENT ----------------- */
function openModal(id) {
  const modal = document.getElementById(id);
  if (modal) {
    modal.classList.add('active');
    // Close capture card dropdown if open
    document.getElementById('captureMenu')?.classList.remove('show');
    document.getElementById('btnCaptureDropdown')?.classList.remove('open');
  }
}

function closeModal(id) {
  const modal = document.getElementById(id);
  if (modal) {
    modal.classList.remove('active');
  }
}

// Close modals when clicking outside modal content
document.addEventListener('click', (e) => {
  if (e.target.classList.contains('modal-backdrop')) {
    e.target.classList.remove('active');
  }
});

// Escape key closes modals and dropdowns
document.addEventListener('keydown', (e) => {
  if (e.key === 'Escape') {
    document.querySelectorAll('.modal-backdrop.active').forEach(m => m.classList.remove('active'));
    document.getElementById('captureMenu')?.classList.remove('show');
    document.getElementById('btnCaptureDropdown')?.classList.remove('open');
  }
});

/* Specific Modal Triggers */
function openNewPatientModal() { openModal('modalNewPatient'); }
function openArchiveModal() { openModal('modalArchive'); }
function openDoctorsModal() { openModal('modalDoctors'); }
function openReferrersModal() { openModal('modalReferrers'); }
function openTemplatesModal() { openModal('modalTemplates'); }
function openSettingsModal() { openModal('modalSettings'); }

function openCaptureModal(action) {
  document.getElementById('captureMenu')?.classList.remove('show');
  document.getElementById('btnCaptureDropdown')?.classList.remove('open');
  
  openModal('modalCaptureCard');
  if (action === 'add') {
    setTimeout(() => alert('Capture Hardware Discovery Wizard:\nScanning PCIe/USB3 slots for unconfigured video capture cards...'), 300);
  } else if (action === 'delete') {
    setTimeout(() => alert('Delete Mode:\nSelect an active device in the table below to unbind.'), 300);
  }
}

/* ----------------- 5. CLINICAL WORKFLOW ACTIONS ----------------- */
function handlePatientSubmit(event) {
  event.preventDefault();
  const name = document.getElementById('patientName').value;
  const mrn = document.getElementById('patientMrn').value;
  const proc = document.getElementById('patientProcedure').value;
  const suite = document.getElementById('patientSuite').value;

  alert(`Patient Registered Successfully!\n\nPatient: ${name} [${mrn}]\nProcedure: ${proc}\nAssigned Room: ${suite}\n\nCapture Card initialized and video acquisition channel online.`);
  closeModal('modalNewPatient');
  event.target.reset();
}

function testActiveSignal() {
  alert('Video Signal Diagnostics:\n- Device: Olympus EVIS X1 PCIe Grabber\n- Resolution: 3840x2160 (4K UHD)\n- Refresh: 59.94 Hz (Rock Solid Lock)\n- Latency: 14ms\n- Status: PASS');
}

function filterArchive() {
  const input = document.getElementById('archiveSearch');
  const filter = input.value.toLowerCase();
  const procFilter = document.getElementById('archiveFilter').value;
  const table = document.getElementById('archiveTable');
  const rows = table.getElementsByTagName('tbody')[0].getElementsByTagName('tr');

  for (let i = 0; i < rows.length; i++) {
    const text = rows[i].textContent.toLowerCase();
    const procText = rows[i].cells[3].textContent;
    
    const matchesSearch = text.includes(filter);
    const matchesProc = (procFilter === 'All Procedures') || procText.includes(procFilter);

    if (matchesSearch && matchesProc) {
      rows[i].style.display = '';
    } else {
      rows[i].style.display = 'none';
    }
  }
}

function toggleMaximize() {
  const shell = document.getElementById('windowShell');
  if (shell.classList.contains('res-fluid')) {
    setResolution('1920');
  } else {
    setResolution('fluid');
  }
}
