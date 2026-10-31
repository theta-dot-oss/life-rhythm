// Service worker: used only so desktop notifications can carry action buttons.
// It does not cache anything; the app always loads the latest files.
self.addEventListener('install', () => self.skipWaiting());
self.addEventListener('activate', e => e.waitUntil(self.clients.claim()));
self.addEventListener('notificationclick', e => {
  e.notification.close();
  const action = e.action || 'open';
  e.waitUntil((async () => {
    const list = await self.clients.matchAll({ type: 'window', includeUncontrolled: true });
    const client = list.find(c => 'focus' in c);
    if (client) {
      try { await client.focus(); } catch (err) {}
      if (action !== 'open') client.postMessage({ type: 'notification-action', action });
    } else {
      await self.clients.openWindow('./' + (action !== 'open' ? '?action=' + encodeURIComponent(action) : ''));
    }
  })());
});
