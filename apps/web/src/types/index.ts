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
  total_posts: number;
  total_comments: number;
  popular_posts: { slug: string; views: number }[];
  page_views_daily: { date: string; count: number }[];
  recent_events: { event_type: string; source_page: string; created_at: string }[];
}

export interface TrackingEvent {
  event_type: string;
  event_data: Record<string, unknown>;
  source_page: string;
  session_id: string;
}
