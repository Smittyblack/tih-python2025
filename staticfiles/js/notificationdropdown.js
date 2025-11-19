document.addEventListener('DOMContentLoaded', function() {
    console.log('DOM fully loaded');
    const notificationsLink = document.getElementById('notifications-link');
    const notificationDropdown = document.getElementById('notification-dropdown');

    if (!notificationsLink || !notificationDropdown) {
        console.error('Elements not found:', {
            link: !!notificationsLink,
            dropdown: !!notificationDropdown
        });
        return;
    }

    notificationsLink.addEventListener('click', function(e) {
        e.preventDefault();
        console.log('Notifications clicked');
        if (notificationDropdown.style.display === 'block') {
            notificationDropdown.style.display = 'none';
        } else {
            notificationDropdown.style.display = 'block';
            fetchInitialNotifications();
            markNotificationsAsRead();
        }
    });

    document.addEventListener('click', function(e) {
        if (!notificationsLink.contains(e.target) && !notificationDropdown.contains(e.target)) {
            notificationDropdown.style.display = 'none';
        }
    });

    function fetchInitialNotifications() {
        fetch('/users/notifications/', {
            method: 'GET',
            headers: {
                'X-Requested-With': 'XMLHttpRequest'
            }
        })
            .then(response => {
                console.log('Fetch status:', response.status);
                if (!response.ok) {
                    return response.text().then(text => {
                        throw new Error(`Network response was not ok: ${response.status} - ${text}`);
                    });
                }
                return response.json();
            })
            .then(data => {
                console.log('Fetched initial notifications:', data);
                const notificationList = document.getElementById('notification-list');
                notificationList.innerHTML = '';
                if (data.notifications && Array.isArray(data.notifications)) {
                    data.notifications.forEach(notif => {
                        const item = document.createElement('div');
                        item.className = 'notification-item';
                        item.innerHTML = `${notif.message} - ${new Date(notif.created_at).toLocaleString()} on <a href="${notif.link}">[Post]</a>`;
                        notificationList.appendChild(item);
                    });
                } else if (data.error) {
                    notificationList.innerHTML = `<div class="notification-item">Error: ${data.error}</div>`;
                } else {
                    notificationList.innerHTML = '<div class="notification-item">No notifications available</div>';
                }
            })
            .catch(error => console.error('Error fetching notifications:', error));
    }

    function markNotificationsAsRead() {
        fetch('/users/notifications/', {
            method: 'POST',
            headers: {
                'X-CSRFToken': document.querySelector('input[name="csrfmiddlewaretoken"]').value,
                'Content-Type': 'application/x-www-form-urlencoded',
                'X-Requested-With': 'XMLHttpRequest'
            },
            body: 'mark_read=true'
        })
            .then(response => {
                console.log('Mark read status:', response.status);
                if (!response.ok) {
                    return response.text().then(text => {
                        throw new Error(`POST failed: ${response.status} - ${text}`);
                    });
                }
                return response.json();
            })
            .then(data => {
                console.log('Mark read response:', data);
                const unreadCount = document.querySelector('.unread-count');
                if (unreadCount) {
                    unreadCount.textContent = '0';
                    unreadCount.style.display = 'none';
                }
            })
            .catch(error => console.error('Error marking notifications as read:', error));
    }

    try {
        const socket = new WebSocket('ws://' + window.location.host + '/ws/notifications/');
        socket.onopen = function(e) {
            console.log('WebSocket connected successfully');
        };
        socket.onmessage = function(e) {
            console.log('WebSocket message received:', e.data);
            const data = JSON.parse(e.data);
            const notificationList = document.getElementById('notification-list');
            const notificationItem = document.createElement('div');
            notificationItem.className = 'notification-item';
            notificationItem.innerHTML = `${data.message} - ${new Date(data.created_at).toLocaleString()} on <a href="${data.link}">${data.post_title || '[Post]'}</a>`;
            notificationList.prepend(notificationItem);
        };
        socket.onclose = function(e) {
            console.error('WebSocket closed:', e.code, e.reason);
        };
        socket.onerror = function(e) {
            console.error('WebSocket error:', e);
        };
    } catch (e) {
        console.error('WebSocket setup failed:', e);
    }
});