 // Функция для выделения всех товаров
    function toggleSelectAll(source) {
        const checkboxes = document.querySelectorAll('input[name="product_ids"]');
        checkboxes.forEach(checkbox => {
            checkbox.checked = source.checked;
        });
    }

    // Функция для закрытия сообщения
    function closeMessage(element) {
        element.classList.add('fade-out');
        setTimeout(() => element.remove(), 500);
    }

    // После загрузки DOM
    document.addEventListener('DOMContentLoaded', () => {
        // Авто-закрытие сообщений
        document.querySelectorAll('#messages-container .alert').forEach(alert => {
            const delay = parseInt(alert.dataset.delay) || 5000;
            setTimeout(() => closeMessage(alert), delay);
        });

        // Ручное закрытие
        document.querySelectorAll('.close-btn').forEach(btn => {
            btn.addEventListener('click', function() {
                closeMessage(this.parentElement);
            });
        });

        // Удаление выбранных товаров
        document.getElementById('delete-selected').addEventListener('click', function() {
            const checkboxes = document.querySelectorAll('input[name="product_ids"]:checked');
            
            if (checkboxes.length === 0) {
                alert('Пожалуйста, выберите хотя бы один товар для удаления.');
                return;
            }

            if (!confirm('Вы уверены, что хотите удалить выбранные товары?')) {
                return;
            }

            const productIds = Array.from(checkboxes).map(cb => cb.value);
            const formData = new FormData();
            formData.append('csrfmiddlewaretoken', '{{ csrf_token }}');
            productIds.forEach(id => formData.append('product_ids', id));

            fetch("{% url 'delete_products' %}", {
                method: 'POST',
                body: formData
            })
            .then(response => {
                if (response.ok) {
                    window.location.reload();
                } else {
                    alert('Ошибка при удалении товаров.');
                }
            })
            .catch(error => {
                console.error('Error:', error);
                alert('Произошла ошибка при удалении товаров.');
            });
        });
    });

document.addEventListener('DOMContentLoaded', function() {
    // Автоматическое скрытие сообщений через 5 секунд
    setTimeout(function() {
        const messages = document.querySelectorAll('.alert');
        messages.forEach(message => {
            message.style.opacity = '0';
            setTimeout(() => {
                message.style.display = 'none';
            }, 500);
        });
    }, 5000);

    // Закрытие сообщений при клике на кнопку
    document.querySelectorAll('.close-btn').forEach(btn => {
        btn.addEventListener('click', function() {
            const message = this.parentElement;
            message.style.opacity = '0';
            setTimeout(() => {
                message.style.display = 'none';
            }, 500);
        });
    });

    // Добавление новых форм материалов
    document.querySelector('#add-material').addEventListener('click', function() {
        const formCount = document.querySelector('#id_materials-TOTAL_FORMS');
        const container = document.querySelector('#materials-formset');
        const totalForms = parseInt(formCount.value);
        
        // Клонируем первую форму
        const newForm = container.querySelector('.formset-item').cloneNode(true);
        
        // Обновляем индексы в ID и name
        newForm.innerHTML = newForm.innerHTML.replace(
            /materials-\d+-/g, 
            `materials-${totalForms}-`
        );
        
        // Очищаем значения
        const nameInput = newForm.querySelector('input[name$="-name"]');
        if (nameInput) nameInput.value = '';
        
        // Убираем скрытое поле ID
        const idInput = newForm.querySelector('input[name$="-id"]');
        if (idInput) idInput.remove();
        
        // Убираем чекбокс удаления
        const deleteCheckbox = newForm.querySelector('input[name$="-DELETE"]');
        if (deleteCheckbox) {
            deleteCheckbox.checked = false;
            deleteCheckbox.closest('.delete-checkbox').style.display = 'none';
        }
        
        container.appendChild(newForm);
        formCount.value = totalForms + 1;
    });
    
    // Добавление новых форм размеров
    document.querySelector('#add-dimension').addEventListener('click', function() {
        const formCount = document.querySelector('#id_dimensions-TOTAL_FORMS');
        const container = document.querySelector('#dimensions-formset');
        const totalForms = parseInt(formCount.value);
        
        // Клонируем первую форму
        const newForm = container.querySelector('.formset-item').cloneNode(true);
        
        // Обновляем индексы в ID и name
        newForm.innerHTML = newForm.innerHTML.replace(
            /dimensions-\d+-/g, 
            `dimensions-${totalForms}-`
        );
        
        // Очищаем значения
        const nameInput = newForm.querySelector('input[name$="-name"]');
        if (nameInput) nameInput.value = '';
        
        const valueInput = newForm.querySelector('input[name$="-value"]');
        if (valueInput) valueInput.value = '';
        
        // Убираем скрытое поле ID
        const idInput = newForm.querySelector('input[name$="-id"]');
        if (idInput) idInput.remove();
        
        // Убираем чекбокс удаления
        const deleteCheckbox = newForm.querySelector('input[name$="-DELETE"]');
        if (deleteCheckbox) {
            deleteCheckbox.checked = false;
            deleteCheckbox.closest('.delete-checkbox').style.display = 'none';
        }
        
        container.appendChild(newForm);
        formCount.value = totalForms + 1;
    });
});