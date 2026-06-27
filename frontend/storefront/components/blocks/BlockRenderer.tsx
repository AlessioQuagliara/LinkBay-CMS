import type { CmsBlock } from '@/storefront/lib/types/brand'
import HeroBlock from './HeroBlock'
import TextBlock from './TextBlock'
import ProductsBlock from './ProductsBlock'
import BannerBlock from './BannerBlock'
import HtmlBlock from './HtmlBlock'
import SpacerBlock from './SpacerBlock'

interface BlockRendererProps {
  blocks: CmsBlock[]
}

export default function BlockRenderer({ blocks }: BlockRendererProps) {
  const sorted = [...blocks].sort((a, b) => a.order - b.order)

  return (
    <>
      {sorted.map((block) => {
        switch (block.type) {
          case 'hero':
            return <HeroBlock key={block.id} settings={block.settings} />
          case 'text':
            return <TextBlock key={block.id} settings={block.settings} />
          case 'products':
            return <ProductsBlock key={block.id} settings={block.settings} />
          case 'banner':
            return <BannerBlock key={block.id} settings={block.settings} />
          case 'html':
            return <HtmlBlock key={block.id} settings={block.settings} />
          case 'spacer':
            return <SpacerBlock key={block.id} settings={block.settings} />
          default:
            return null
        }
      })}
    </>
  )
}
