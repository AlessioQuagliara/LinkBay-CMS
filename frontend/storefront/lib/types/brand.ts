export interface SocialLinks {
  instagram?: string
  facebook?: string
  twitter?: string
  tiktok?: string
  youtube?: string
  linkedin?: string
  [key: string]: string | undefined
}

export interface Brand {
  store_name: string
  tagline: string | null
  logo_url: string | null
  favicon_url: string | null
  primary_color: string
  secondary_color: string
  accent_color: string | null
  font_heading: string | null
  font_body: string | null
  contact_email: string | null
  phone: string | null
  address: string | null
  currency: string
  locale: string
  social_links: SocialLinks
  meta_title: string | null
  meta_description: string | null
}

export interface CmsBlock {
  id: string
  type:
    | 'hero'
    | 'text'
    | 'products'
    | 'banner'
    | 'html'
    | 'spacer'
    | 'image'
    | 'video'
  settings: Record<string, unknown>
  order: number
}

export interface CmsPage {
  id: number
  title: string
  slug: string
  blocks: CmsBlock[]
  visibility: 'public' | 'hidden' | 'password_protected'
  is_homepage: boolean
  meta_title: string | null
  meta_description: string | null
  published_at: string | null
}
