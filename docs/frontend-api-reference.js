/**
 * Sound of Hope Foundation — Frontend API Reference
 * Base URL: http://localhost:8000/api/v1  (development)
 *
 * Authentication:
 *   - Login returns { access_token, refresh_token, token_type, expires_in }
 *   - Pass access_token as:  Authorization: Bearer <access_token>
 *   - access_token expires in 30 minutes. Use /auth/refresh to get a new one.
 *
 * Paginated responses have this shape:
 *   {
 *     items: [...],
 *     meta: { page, page_size, total, total_pages }
 *   }
 *   Query params: ?page=1&page_size=20
 */

const BASE_URL = "http://localhost:8000/api/v1";

// ─────────────────────────────────────────────────────────────
// HELPERS
// ─────────────────────────────────────────────────────────────

function getToken() {
  return localStorage.getItem("access_token");
}

async function apiFetch(path, options = {}) {
  const headers = {
    "Content-Type": "application/json",
    ...(getToken() ? { Authorization: `Bearer ${getToken()}` } : {}),
    ...options.headers,
  };
  const res = await fetch(`${BASE_URL}${path}`, { ...options, headers });
  if (!res.ok) {
    const error = await res.json().catch(() => ({ detail: res.statusText }));
    throw { status: res.status, detail: error.detail ?? error };
  }
  if (res.status === 204) return null;
  return res.json();
}


// ─────────────────────────────────────────────────────────────
// AUTHENTICATION  —  /api/v1/auth
// ─────────────────────────────────────────────────────────────

/**
 * Register a new user account.
 * Password must have uppercase, lowercase, and a digit.
 *
 * @param {{ email, password, first_name, last_name, phone? }} body
 * @returns {Promise<{ id, email, is_active, is_email_verified, first_name, last_name, created_at }>}
 */
export async function register(body) {
  return apiFetch("/auth/register", {
    method: "POST",
    body: JSON.stringify(body),
  });
}

/**
 * Log in and receive tokens.
 *
 * @param {{ email, password }} body
 * @returns {Promise<{ access_token, refresh_token, token_type, expires_in }>}
 *
 * @example
 *   const tokens = await login({ email: "admin@soundofhope.org", password: "AdminPass1!" });
 *   localStorage.setItem("access_token", tokens.access_token);
 *   localStorage.setItem("refresh_token", tokens.refresh_token);
 */
export async function login(body) {
  return apiFetch("/auth/login", {
    method: "POST",
    body: JSON.stringify(body),
  });
}

/**
 * Exchange a refresh token for a new access token.
 *
 * @param {string} refreshToken
 * @returns {Promise<{ access_token, refresh_token, token_type, expires_in }>}
 */
export async function refreshToken(refreshToken) {
  return apiFetch("/auth/refresh", {
    method: "POST",
    body: JSON.stringify({ refresh_token: refreshToken }),
  });
}

/**
 * Log out (invalidates the refresh token).
 *
 * @param {string} refreshToken
 */
export async function logout(refreshToken) {
  return apiFetch("/auth/logout", {
    method: "POST",
    body: JSON.stringify({ refresh_token: refreshToken }),
  });
}

/**
 * Log out from all devices.
 */
export async function logoutAll() {
  return apiFetch("/auth/logout-all", { method: "POST" });
}

/**
 * Get the currently authenticated user.
 *
 * @returns {Promise<{ id, email, is_active, is_email_verified, first_name, last_name, created_at }>}
 */
export async function getMe() {
  return apiFetch("/auth/me");
}

/**
 * Verify email using token from the verification email link.
 *
 * @param {string} token
 */
export async function verifyEmail(token) {
  return apiFetch("/auth/verify-email", {
    method: "POST",
    body: JSON.stringify({ token }),
  });
}

/**
 * Resend the email verification link.
 *
 * @param {string} email
 */
export async function resendVerification(email) {
  return apiFetch("/auth/resend-verification", {
    method: "POST",
    body: JSON.stringify({ email }),
  });
}

/**
 * Request a password reset email.
 *
 * @param {string} email
 */
export async function requestPasswordReset(email) {
  return apiFetch("/auth/password/reset", {
    method: "POST",
    body: JSON.stringify({ email }),
  });
}

/**
 * Complete a password reset using the token from the reset email.
 *
 * @param {{ token, new_password }} body
 */
export async function confirmPasswordReset(body) {
  return apiFetch("/auth/password/reset/confirm", {
    method: "POST",
    body: JSON.stringify(body),
  });
}

/**
 * Change password while authenticated.
 *
 * @param {{ current_password, new_password }} body
 */
export async function changePassword(body) {
  return apiFetch("/auth/password/change", {
    method: "POST",
    body: JSON.stringify(body),
  });
}


// ─────────────────────────────────────────────────────────────
// CMS PAGES  —  /api/v1/cms/pages
// Content for landing pages (hero, about, programmes, etc.)
// Each page has a slug and flexible content_blocks JSON.
// ─────────────────────────────────────────────────────────────

/**
 * List all CMS pages.
 *
 * @param {{ status?: "draft"|"published"|"archived", page?: number, page_size?: number }} params
 * @returns {Promise<{ items: Page[], meta: PageMeta }>}
 *
 * Page shape:
 *   { id, slug, title, meta_description, status, published_at, created_at }
 */
export async function listPages({ status, page = 1, page_size = 20 } = {}) {
  const q = new URLSearchParams({ page, page_size });
  if (status) q.set("status", status);
  return apiFetch(`/cms/pages?${q}`);
}

/**
 * Get a single CMS page by ID.
 *
 * @param {string} pageId  UUID
 * @returns {Promise<{ id, slug, title, meta_description, status, published_at, created_at }>}
 */
export async function getPage(pageId) {
  return apiFetch(`/cms/pages/${pageId}`);
}

/**
 * Create a new CMS page. Requires CONTENT_CREATE permission.
 *
 * @param {{ slug, title, meta_description? }} body
 *   slug examples: "home", "about", "programmes", "contact"
 * @returns {Promise<Page>}
 */
export async function createPage(body) {
  return apiFetch("/cms/pages", {
    method: "POST",
    body: JSON.stringify(body),
  });
}

/**
 * Update page metadata (title or meta_description). Requires CONTENT_MANAGE.
 *
 * @param {string} pageId
 * @param {{ title?, meta_description? }} body
 * @returns {Promise<Page>}
 */
export async function updatePage(pageId, body) {
  return apiFetch(`/cms/pages/${pageId}`, {
    method: "PATCH",
    body: JSON.stringify(body),
  });
}

/**
 * Save a new content version for a page. Requires CONTENT_MANAGE.
 * content_blocks is a free-form JSON object — structure it however the
 * frontend needs (sections, hero, cards, etc.).
 *
 * @param {string} pageId
 * @param {{ content_blocks: object }} body
 * @returns {Promise<{ id, page_id, version_number, content_blocks, created_at }>}
 *
 * @example
 *   await createPageVersion(pageId, {
 *     content_blocks: {
 *       hero: { heading: "Transforming Lives Through Music", subtext: "...", image_url: "..." },
 *       intro: { body: "Sound of Hope Foundation..." },
 *       stats: [{ label: "Participants", value: "1,200+" }],
 *     }
 *   });
 */
export async function createPageVersion(pageId, body) {
  return apiFetch(`/cms/pages/${pageId}/versions`, {
    method: "POST",
    body: JSON.stringify(body),
  });
}

/**
 * List all versions of a page. Requires CONTENT_READ.
 *
 * @param {string} pageId
 * @returns {Promise<Array<{ id, page_id, version_number, content_blocks, created_at }>>}
 */
export async function listPageVersions(pageId) {
  return apiFetch(`/cms/pages/${pageId}/versions`);
}

/**
 * Publish a page (makes it live). Requires CONTENT_PUBLISH.
 *
 * @param {string} pageId
 * @returns {Promise<Page>}
 */
export async function publishPage(pageId) {
  return apiFetch(`/cms/pages/${pageId}/publish`, { method: "POST" });
}

/**
 * Archive a page. Requires CONTENT_MANAGE.
 *
 * @param {string} pageId
 * @returns {Promise<Page>}
 */
export async function archivePage(pageId) {
  return apiFetch(`/cms/pages/${pageId}/archive`, { method: "POST" });
}


// ─────────────────────────────────────────────────────────────
// PUBLICATIONS  —  /api/v1/publications
// Articles, reports, newsletters, policies, research papers.
// Shown in the News / Resources section of the landing page.
// ─────────────────────────────────────────────────────────────

/**
 * List publications.
 * For the public landing page, always pass is_published=true&is_public=true.
 *
 * @param {{
 *   publication_type?: "article"|"report"|"newsletter"|"policy"|"research",
 *   is_published?: boolean,
 *   is_public?: boolean,
 *   page?: number,
 *   page_size?: number
 * }} params
 * @returns {Promise<{ items: Publication[], meta: PageMeta }>}
 *
 * Publication shape:
 *   { id, title, publication_type, summary, published_date, is_published, is_public, file_key, created_at }
 */
export async function listPublications({
  publication_type,
  is_published,
  is_public,
  page = 1,
  page_size = 20,
} = {}) {
  const q = new URLSearchParams({ page, page_size });
  if (publication_type) q.set("publication_type", publication_type);
  if (is_published !== undefined) q.set("is_published", is_published);
  if (is_public !== undefined) q.set("is_public", is_public);
  return apiFetch(`/publications?${q}`);
}

/**
 * Get a single publication by ID. Requires PUBLICATION_READ.
 *
 * @param {string} publicationId  UUID
 * @returns {Promise<Publication>}
 */
export async function getPublication(publicationId) {
  return apiFetch(`/publications/${publicationId}`);
}

/**
 * Create a publication. Requires PUBLICATION_MANAGE.
 *
 * @param {{
 *   title,
 *   publication_type?: "article"|"report"|"newsletter"|"policy"|"research",
 *   summary?,
 *   body?,
 *   published_date?,   // "YYYY-MM-DD"
 *   is_public?
 * }} body
 * @returns {Promise<Publication>}
 */
export async function createPublication(body) {
  return apiFetch("/publications", {
    method: "POST",
    body: JSON.stringify(body),
  });
}

/**
 * Update a publication. Requires CONTENT_MANAGE.
 *
 * @param {string} publicationId
 * @param {{ title?, summary?, body?, published_date?, is_public? }} body
 * @returns {Promise<Publication>}
 */
export async function updatePublication(publicationId, body) {
  return apiFetch(`/publications/${publicationId}`, {
    method: "PATCH",
    body: JSON.stringify(body),
  });
}

/**
 * Publish a publication (sets is_published=true). Requires CONTENT_PUBLISH.
 *
 * @param {string} publicationId
 * @returns {Promise<Publication>}
 */
export async function publishPublication(publicationId) {
  return apiFetch(`/publications/${publicationId}/publish`, { method: "POST" });
}

/**
 * Delete a publication. Requires CONTENT_MANAGE.
 *
 * @param {string} publicationId
 * @returns {Promise<null>}
 */
export async function deletePublication(publicationId) {
  return apiFetch(`/publications/${publicationId}`, { method: "DELETE" });
}


// ─────────────────────────────────────────────────────────────
// EVENTS  —  /api/v1/events
// Public events shown on the landing page. No auth required for
// listing and viewing. Registration is also open.
// ─────────────────────────────────────────────────────────────

/**
 * List events. No authentication required.
 * For the public landing page, pass is_public=true.
 *
 * @param {{
 *   is_public?: boolean,
 *   from_date?: string,  // ISO datetime e.g. "2026-01-01T00:00:00"
 *   page?: number,
 *   page_size?: number
 * }} params
 * @returns {Promise<{ items: Event[], meta: PageMeta }>}
 *
 * Event shape:
 *   { id, title, description, event_type, location, is_online, starts_at,
 *     ends_at, max_attendees, is_public, is_published, created_at }
 *
 * event_type: "general" | "workshop" | "concert" | "exhibition" | "community" | "training"
 */
export async function listEvents({ is_public, from_date, page = 1, page_size = 20 } = {}) {
  const q = new URLSearchParams({ page, page_size });
  if (is_public !== undefined) q.set("is_public", is_public);
  if (from_date) q.set("from_date", from_date);
  return apiFetch(`/events?${q}`);
}

/**
 * Get a single event by ID. No authentication required.
 *
 * @param {string} eventId  UUID
 * @returns {Promise<Event>}
 */
export async function getEvent(eventId) {
  return apiFetch(`/events/${eventId}`);
}

/**
 * Register for an event. No authentication required.
 * Pass participant_id or user_id if known, otherwise both can be null
 * for anonymous walk-in registrations.
 *
 * @param {string} eventId
 * @param {{ participant_id?: string, user_id?: string, notes?: string }} body
 * @returns {Promise<{ id, event_id, participant_id, user_id, status, attended, created_at }>}
 */
export async function registerForEvent(eventId, body = {}) {
  return apiFetch(`/events/${eventId}/register`, {
    method: "POST",
    body: JSON.stringify(body),
  });
}

/**
 * Create an event. Requires EVENT_CREATE permission.
 *
 * @param {{
 *   title,
 *   description?,
 *   event_type?: "general"|"workshop"|"concert"|"exhibition"|"community"|"training",
 *   location?,
 *   is_online?,
 *   online_link?,
 *   starts_at,       // ISO datetime
 *   ends_at,         // ISO datetime — must be after starts_at
 *   max_attendees?,
 *   is_public?
 * }} body
 * @returns {Promise<Event>}
 */
export async function createEvent(body) {
  return apiFetch("/events", {
    method: "POST",
    body: JSON.stringify(body),
  });
}

/**
 * Update an event. Requires EVENT_MANAGE permission.
 *
 * @param {string} eventId
 * @param {{ title?, description?, location?, starts_at?, ends_at?, max_attendees?, is_public? }} body
 * @returns {Promise<Event>}
 */
export async function updateEvent(eventId, body) {
  return apiFetch(`/events/${eventId}`, {
    method: "PATCH",
    body: JSON.stringify(body),
  });
}

/**
 * Publish an event (makes it visible on the landing page). Requires EVENT_MANAGE.
 *
 * @param {string} eventId
 * @returns {Promise<Event>}
 */
export async function publishEvent(eventId) {
  return apiFetch(`/events/${eventId}/publish`, { method: "POST" });
}

/**
 * List registrations for an event. Requires EVENT_READ permission.
 *
 * @param {string} eventId
 * @returns {Promise<Array<{ id, event_id, participant_id, user_id, status, attended, created_at }>>}
 */
export async function listEventRegistrations(eventId) {
  return apiFetch(`/events/${eventId}/registrations`);
}


// ─────────────────────────────────────────────────────────────
// MEDIA  —  /api/v1/media
// Upload images and files used in CMS pages and publications.
// ─────────────────────────────────────────────────────────────

/**
 * Upload a media file. Requires MEDIA_UPLOAD permission.
 * Use this to upload images for hero banners, publication covers, etc.
 * The returned storage_key is what you store in content_blocks.
 *
 * @param {File} file         Browser File object
 * @param {string} folder     e.g. "hero", "publications", "events", "general"
 * @param {string} [altText]  Accessibility alt text
 * @returns {Promise<{
 *   id, storage_key, original_filename, mime_type, file_size, alt_text, folder, created_at
 * }>}
 *
 * @example
 *   const input = document.querySelector('input[type="file"]');
 *   const asset = await uploadMedia(input.files[0], "hero", "Children learning music");
 *   // Use asset.storage_key inside your CMS content_blocks
 */
export async function uploadMedia(file, folder = "general", altText = null) {
  const formData = new FormData();
  formData.append("file", file);
  formData.append("folder", folder);
  if (altText) formData.append("alt_text", altText);

  const res = await fetch(`${BASE_URL}/media/upload`, {
    method: "POST",
    headers: { Authorization: `Bearer ${getToken()}` },
    // Do NOT set Content-Type — the browser sets it with the boundary for multipart
    body: formData,
  });
  if (!res.ok) {
    const error = await res.json().catch(() => ({ detail: res.statusText }));
    throw { status: res.status, detail: error.detail ?? error };
  }
  return res.json();
}

/**
 * List uploaded media assets. Requires MEDIA_MANAGE permission.
 *
 * @param {{ folder?: string, page?: number, page_size?: number }} params
 * @returns {Promise<{ items: MediaAsset[], meta: PageMeta }>}
 */
export async function listMedia({ folder, page = 1, page_size = 20 } = {}) {
  const q = new URLSearchParams({ page, page_size });
  if (folder) q.set("folder", folder);
  return apiFetch(`/media?${q}`);
}

/**
 * Delete a media asset. Requires MEDIA_MANAGE permission.
 *
 * @param {string} assetId  UUID
 * @returns {Promise<null>}
 */
export async function deleteMedia(assetId) {
  return apiFetch(`/media/${assetId}`, { method: "DELETE" });
}


// ─────────────────────────────────────────────────────────────
// TYPICAL LANDING PAGE BOOTSTRAP
// Call this on initial page load to hydrate all landing page sections.
// ─────────────────────────────────────────────────────────────

/**
 * Fetch everything needed to render the public landing page in one shot.
 * All requests run in parallel.
 *
 * @returns {Promise<{ pages, news, articles, events }>}
 *
 * @example
 *   const { pages, news, articles, events } = await getLandingPageData();
 *
 *   // Find specific pages by slug:
 *   const homePage    = pages.items.find(p => p.slug === "home");
 *   const aboutPage   = pages.items.find(p => p.slug === "about");
 *
 *   // Render news feed:
 *   news.items.forEach(pub => renderArticleCard(pub));
 *
 *   // Render upcoming events:
 *   events.items.forEach(evt => renderEventCard(evt));
 */
export async function getLandingPageData() {
  const now = new Date().toISOString();

  const [pages, news, articles, events] = await Promise.all([
    listPages({ status: "published" }),
    listPublications({ is_published: true, is_public: true, publication_type: "newsletter", page_size: 5 }),
    listPublications({ is_published: true, is_public: true, publication_type: "article", page_size: 6 }),
    listEvents({ is_public: true, from_date: now, page_size: 6 }),
  ]);

  return { pages, news, articles, events };
}
