/**
 * Touch and Solve Micro Finance UI JavaScript
 */

document.addEventListener('DOMContentLoaded', () => {
  // Global 3-Bar Sidebar functions
  window.openSidebar = function(e) {
    if (e) { e.preventDefault(); e.stopPropagation(); }
    const sidebar = document.getElementById('app-sidebar');
    const backdrop = document.getElementById('sidebar-backdrop');
    if (sidebar) sidebar.classList.add('show');
    if (backdrop) backdrop.classList.add('show');
    document.body.style.overflow = 'hidden';
  };

  window.closeSidebar = function(e) {
    if (e) { e.preventDefault(); e.stopPropagation(); }
    const sidebar = document.getElementById('app-sidebar');
    const backdrop = document.getElementById('sidebar-backdrop');
    if (sidebar) sidebar.classList.remove('show');
    if (backdrop) backdrop.classList.remove('show');
    document.body.style.overflow = '';
  };

  window.toggleSidebar = function(e) {
    if (e) { e.preventDefault(); e.stopPropagation(); }
    const sidebar = document.getElementById('app-sidebar');
    if (sidebar && sidebar.classList.contains('show')) {
      window.closeSidebar(e);
    } else {
      window.openSidebar(e);
    }
  };

  const sidebarToggleBtn = document.getElementById('sidebar-toggle-btn');
  const sidebarCloseBtn = document.getElementById('sidebar-close-btn');
  const sidebarBackdrop = document.getElementById('sidebar-backdrop');

  if (sidebarToggleBtn) sidebarToggleBtn.onclick = window.toggleSidebar;
  if (sidebarCloseBtn) sidebarCloseBtn.onclick = window.closeSidebar;
  if (sidebarBackdrop) sidebarBackdrop.onclick = window.closeSidebar;

  document.addEventListener('keydown', (e) => {
    if (e.key === 'Escape') {
      window.closeSidebar();
    }
  });

  // Notification Bell Toggle
  const bellBtn = document.getElementById('notif-bell-btn');
  const notifDropdown = document.getElementById('notif-dropdown');

  if (bellBtn && notifDropdown) {
    bellBtn.addEventListener('click', (e) => {
      e.stopPropagation();
      notifDropdown.classList.toggle('show');
    });

    document.addEventListener('click', (e) => {
      if (!notifDropdown.contains(e.target) && !bellBtn.contains(e.target)) {
        notifDropdown.classList.remove('show');
      }
    });
  }

  // Modal Open/Close handler
  window.openModal = function (modalId) {
    const modal = document.getElementById(modalId);
    if (modal) {
      modal.classList.add('active');
    }
  };

  window.closeModal = function (modalId) {
    const modal = document.getElementById(modalId);
    if (modal) {
      modal.classList.remove('active');
    }
  };

  // Close modals when clicking on backdrop
  document.querySelectorAll('.modal-backdrop').forEach((backdrop) => {
    backdrop.addEventListener('click', (e) => {
      if (e.target === backdrop) {
        backdrop.classList.remove('active');
      }
    });
  });

  // Dynamic Loan Calculator for Loan Application form
  const amountInput = document.querySelector('input[name="principal_amount"]');
  const durationInput = document.querySelector('input[name="duration_months"]');
  const calcResult = document.getElementById('loan-calc-summary');

  function updateLoanCalculation() {
    if (!amountInput || !durationInput || !calcResult) return;
    const amount = parseFloat(amountInput.value) || 0;
    const months = parseInt(durationInput.value) || 12;
    const rate = 10.0; // 10% flat interest

    if (amount > 0 && months > 0) {
      const interest = (amount * (rate / 100) * (months / 12));
      const totalPayable = amount + interest;
      const monthlyInstallment = totalPayable / months;

      calcResult.innerHTML = `
        <div style="background: #f8fafc; border: 1px solid #e2e8f0; border-radius: 8px; padding: 12px; margin-top: 10px; font-size: 0.85rem;">
          <div style="display: flex; justify-content: space-between; margin-bottom: 4px;">
            <span style="color: #64748b;">Principal:</span> <strong>${amount.toLocaleString()} BDT</strong>
          </div>
          <div style="display: flex; justify-content: space-between; margin-bottom: 4px;">
            <span style="color: #64748b;">Est. Interest (${rate}%):</span> <strong>${interest.toFixed(2)} BDT</strong>
          </div>
          <div style="display: flex; justify-content: space-between; margin-bottom: 4px;">
            <span style="color: #64748b;">Total Repayable:</span> <strong style="color: #2563eb;">${totalPayable.toFixed(2)} BDT</strong>
          </div>
          <div style="display: flex; justify-content: space-between;">
            <span style="color: #64748b;">Monthly Installment:</span> <strong style="color: #059669;">${monthlyInstallment.toFixed(2)} BDT/mo</strong>
          </div>
        </div>
      `;
    }
  }

  if (amountInput) amountInput.addEventListener('input', updateLoanCalculation);
  if (durationInput) durationInput.addEventListener('input', updateLoanCalculation);
});
