export interface Tag {
  id: string;
  name: string;
  slug: string;
  post_count?: number;
}

export interface PostListItem {
  id: string;
  title: string;
  slug: string;
  excerpt: string | null;
  cover_image: string | null;
  published: boolean;
  featured: boolean;
  view_count: number;
  created_at: string;
  updated_at: string;
  tags: Tag[];
}

export interface PostDetail {
  id: string;
  title: string;
  slug: string;
  content: string;
  excerpt: string | null;
  cover_image: string | null;
  featured: boolean;
  view_count: number;
  created_at: string;
  updated_at: string;
  tags: Tag[];
  prev_post: PostListItem | null;
  next_post: PostListItem | null;
}

export interface PaginatedResponse<T> {
  items: T[];
  total: number;
  page: number;
  size: number;
  pages: number;
}

export interface Comment {
  id: string;
  post_id: string;
  author: string;
  content: string;
  created_at: string;
  status?: string;
  post_title?: string;
  parent_id?: string;
}

export interface ChatMessage {
  role: "user" | "assistant" | "system";
  content: string;
}

export interface ChatResponse {
  answer: string;
  sources: SourceCitation[];
  session_id: string;
}

export interface SourceCitation {
  post_id: string;
  post_title: string;
  post_slug: string;
  chunk_text: string;
}

export interface AnalyticsOverview {
  total_page_views: number;
  today_page_views: number;
  today_unique_visitors: number;
  total_posts: number;
  total_comments: number;
  pending_comments: number;
  pv_trend: number;
  uv_trend: number;
  posts_trend: number;
  comments_trend: number;
  popular_posts: { slug: string; title?: string; views: number }[];
  top_tags: { name: string; slug: string; post_count: number }[];
  page_views_daily: { date: string; count: number }[];
  recent_events: { event_type: string; source_page: string; created_at: string }[];
}

export interface AnalyticsTrend {
  labels: string[];
  datasets: Array<{
    label: string;
    data: number[];
  }>;
}

export interface RealtimeStats {
  online_users: number;
  active_sessions: number;
}

export interface TrackingEvent {
  event_type: string;
  event_data: Record<string, unknown>;
  source_page: string;
  session_id: string;
}

export interface MediaItem {
  id: string;
  filename: string;
  url: string;
  mime_type: string;
  size: number;
  created_at: string;
}

export interface AdminPostListItem extends PostListItem {
  published: boolean;
}

export interface ChangePasswordPayload {
  old_password: string;
  new_password: string;
}

export interface TagCreatePayload {
  name: string;
  slug: string;
}

export interface TagUpdatePayload {
  name?: string;
  slug?: string;
}

export interface BatchActionPayload {
  ids: string[];
}

export interface RefreshTokenResponse {
  access_token: string;
  refresh_token: string;
  token_type: string;
}

export interface PostCreate {
  title: string;
  slug: string;
  content: string;
  excerpt?: string | null;
  cover_image?: string | null;
  published?: boolean;
  featured?: boolean;
  tag_ids?: string[];
}

export interface PostUpdate {
  title?: string;
  slug?: string;
  content?: string;
  excerpt?: string | null;
  cover_image?: string | null;
  published?: boolean;
  featured?: boolean;
  tag_ids?: string[];
}
