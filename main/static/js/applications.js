document.addEventListener('DOMContentLoaded', function() {
    /* =========================
       Обработчики событий
       ========================= */
    // Обработчик изменения статуса через select
    document.querySelectorAll('.status-select').forEach(select => {
        select.addEventListener('change', function() {
            const appId = this.dataset.appId;
            const status = this.value;
            const badge = this.closest('tr').querySelector('.badge'); // На случай, если оставим badge

            updateApplicationStatus(appId, status, badge);
        });
    });

    const table = document.getElementById('applications-table');

    table.addEventListener('click', function(e) {
        const row = e.target.closest('tr');
        if (!row) return;

        const appId = row.dataset.appId;

        // Кнопка редактирования
        if (e.target.closest('.edit-btn')) {
            enableEditMode(row);
        }

        // Кнопка сохранения
        if (e.target.closest('.save-btn')) {
            saveChanges(row, appId);
        }

        // Кнопка отмены
        if (e.target.closest('.cancel-btn')) {
            disableEditMode(row);
        }

        // Кнопка удаления
        if (e.target.closest('.delete-btn')) {
            e.preventDefault();
            e.stopPropagation();
            
            if (confirm('Вы уверены, что хотите удалить эту заявку? Это действие нельзя отменить.')) {
                deleteApplication(appId);
            }
        }
    });

    /* =========================
       Режим редактирования
       ========================= */
    function enableEditMode(row) {
        row.classList.add('editing');
        row.querySelectorAll('.view-mode').forEach(el => el.style.display = 'none');
        row.querySelectorAll('.edit-mode').forEach(el => el.style.display = '');
        row.querySelector('.edit-btn').style.display = 'none';
        row.querySelector('.save-btn').style.display = '';
        row.querySelector('.cancel-btn').style.display = '';
    }

    function disableEditMode(row) {
        row.classList.remove('editing');
        row.querySelectorAll('.view-mode').forEach(el => el.style.display = '');
        row.querySelectorAll('.edit-mode').forEach(el => el.style.display = 'none');
        row.querySelector('.edit-btn').style.display = '';
        row.querySelector('.save-btn').style.display = 'none';
        row.querySelector('.cancel-btn').style.display = 'none';
    }

    /* =========================
       Сохранение изменений
       ========================= */
    function saveChanges(row, appId) {
        const formData = new FormData();

        // Собираем данные из полей редактирования
        row.querySelectorAll('.edit-mode input, .edit-mode select').forEach(field => {
            formData.append(field.name, field.value);
        });

        // Добавляем CSRF токен
        const csrfToken = document.querySelector('[name=csrfmiddlewaretoken]').value;
        formData.append('csrfmiddlewaretoken', csrfToken);

        // Отправляем на сервер
        fetch(`/applications/${appId}/update/`, {
            method: 'POST',
            body: formData,
            headers: { 'X-Requested-With': 'XMLHttpRequest' }
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                // Обновляем данные в режиме просмотра
                row.querySelector('td:nth-child(1)').textContent = data.fields.name;
                row.querySelector('td:nth-child(2)').textContent = data.fields.email;
                row.querySelector('td:nth-child(3)').textContent = data.fields.phone;
                row.querySelector('td:nth-child(4)').textContent = data.fields.service_display;

                // Обновляем статус
                const statusBadge = row.querySelector('td:nth-child(6) .badge');
                if (data.fields.is_processed) {
                    statusBadge.className = 'badge bg-success';
                    statusBadge.textContent = 'Обработано';
                } else {
                    statusBadge.className = 'badge bg-warning text-dark';
                    statusBadge.textContent = 'В ожидании';
                }

                disableEditMode(row);

                // Показываем уведомление
                showToast('Заявка успешно обновлена', 'success');
            } else {
                showToast('Ошибка при обновлении', 'danger');
            }
        })
        .catch(error => {
            console.error('Error:', error);
            showToast('Ошибка при обновлении', 'danger');
        });
    }

    /* =========================
       Обновление статуса
       ========================= */
    function updateApplicationStatus(appId, status, badgeElement) {
        // Подготавливаем данные для отправки
        const formData = new FormData();
        formData.append('status', status);

        // Добавляем CSRF токен с проверкой его наличия
        const csrfToken = document.querySelector('[name=csrfmiddlewaretoken]').value;
        if (!csrfToken) {
            showToast('Ошибка CSRF токена', 'danger');
            return;
        }
        formData.append('csrfmiddlewaretoken', csrfToken);

        // Отправляем запрос на сервер
        fetch(`/applications/${appId}/update-status/`, {
            method: 'POST',
            body: formData,
            headers: {
                'X-Requested-With': 'XMLHttpRequest',
                'Accept': 'application/json'
            }
        })
        .then(response => {
            if (!response.ok) {
                return response.json().then(err => {
                    console.error('Server error:', err);
                    throw new Error(err.error || 'Ошибка сервера');
                });
            }
            return response.json();
        })
        .then(data => {
            if (data.success) {
                // Обновляем выбранный статус в select (на случай, если сервер вернул другой статус)
                const select = document.querySelector(`.status-select[data-app-id="${appId}"]`);
                if (select) {
                    select.value = data.status;
                }

                showToast('Статус успешно обновлен', 'success');
            } else {
                throw new Error(data.error || 'Не удалось обновить статус');
            }
        })
        .catch(error => {
            console.error('Update status error:', error);
            showToast(error.message || 'Ошибка при обновлении статуса', 'danger');

            // Возвращаем предыдущее значение в select
            const select = document.querySelector(`.status-select[data-app-id="${appId}"]`);
            if (select && badgeElement) {
                select.value = badgeElement.dataset.previousStatus;
            }
        });
    }

    /* =========================
       Удаление заявки
       ========================= */
    function deleteApplication(appId) {
        const formData = new FormData();
        const csrfToken = document.querySelector('[name=csrfmiddlewaretoken]').value;
        
        formData.append('csrfmiddlewaretoken', csrfToken);

        fetch(`/applications/${appId}/delete/`, {
            method: 'POST',
            body: formData,
            headers: {
                'X-Requested-With': 'XMLHttpRequest'
            }
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                // Удаляем строку из таблицы
                const row = document.querySelector(`tr[data-app-id="${appId}"]`);
                if (row) {
                    row.remove();
                }
                
                // Показываем сообщение об успехе
                showToast('Заявка успешно удалена', 'success');
            } else {
                throw new Error(data.error || 'Ошибка при удалении');
            }
        })
        .catch(error => {
            console.error('Error:', error);
            showToast('Ошибка при удалении заявки', 'danger');
        });
    }

    /* =========================
       Уведомления
       ========================= */
    function showToast(message, type) {
        const toast = document.createElement('div');
        toast.className = `toast align-items-center text-white bg-${type} border-0 show`;
        toast.style.position = 'fixed';
        toast.style.bottom = '20px';
        toast.style.right = '20px';
        toast.style.zIndex = '1100';

        toast.innerHTML = `
            <div class="d-flex">
                <div class="toast-body">${message}</div>
                <button type="button" class="btn-close btn-close-white me-2 m-auto" data-bs-dismiss="toast"></button>
            </div>
        `;

        document.body.appendChild(toast);

        setTimeout(() => {
            toast.remove();
        }, 3000);
    }
});