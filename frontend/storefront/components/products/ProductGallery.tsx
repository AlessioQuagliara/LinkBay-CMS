'use client'

import { useState } from 'react'
import Image from 'next/image'
import { Swiper, SwiperSlide } from 'swiper/react'
import { Navigation, Pagination, Zoom } from 'swiper/modules'
import 'swiper/css'
import 'swiper/css/navigation'
import 'swiper/css/pagination'
import 'swiper/css/zoom'
import type { ProductImage } from '@/storefront/lib/types/product'

interface ProductGalleryProps {
  images: ProductImage[]
  productName: string
}

export default function ProductGallery({ images, productName }: ProductGalleryProps) {
  const [activeIndex, setActiveIndex] = useState(0)

  const sorted = [...images].sort((a, b) => {
    if (a.is_primary && !b.is_primary) return -1
    if (!a.is_primary && b.is_primary) return 1
    return a.sort_order - b.sort_order
  })

  if (sorted.length === 0) {
    return (
      <div className="flex aspect-square items-center justify-center rounded-2xl bg-gray-100 text-gray-300">
        <svg
          xmlns="http://www.w3.org/2000/svg"
          className="h-24 w-24"
          fill="none"
          viewBox="0 0 24 24"
          stroke="currentColor"
          aria-label="Nessuna immagine disponibile"
        >
          <path
            strokeLinecap="round"
            strokeLinejoin="round"
            strokeWidth={1}
            d="M4 16l4.586-4.586a2 2 0 012.828 0L16 16m-2-2l1.586-1.586a2 2 0 012.828 0L20 14m-6-6h.01M6 20h12a2 2 0 002-2V6a2 2 0 00-2-2H6a2 2 0 00-2 2v12a2 2 0 002 2z"
          />
        </svg>
      </div>
    )
  }

  return (
    <div className="space-y-3">
      {/* Main slider */}
      <div className="overflow-hidden rounded-2xl">
        <Swiper
          modules={[Navigation, Pagination, Zoom]}
          navigation
          pagination={{ clickable: true }}
          zoom={{ maxRatio: 2.5 }}
          onSlideChange={(s) => setActiveIndex(s.activeIndex)}
          className="aspect-square"
        >
          {sorted.map((img, i) => (
            <SwiperSlide key={img.id}>
              <div className="swiper-zoom-container h-full w-full">
                <Image
                  src={img.url}
                  alt={img.alt_text ?? `${productName} — immagine ${i + 1}`}
                  fill
                  priority={i === 0}
                  sizes="(max-width: 768px) 100vw, 50vw"
                  className="object-cover"
                />
              </div>
            </SwiperSlide>
          ))}
        </Swiper>
      </div>

      {/* Thumbnails */}
      {sorted.length > 1 && (
        <div className="flex gap-2 overflow-x-auto pb-1" role="list" aria-label="Miniature immagini">
          {sorted.map((img, i) => (
            <button
              key={img.id}
              role="listitem"
              aria-label={`Vai all'immagine ${i + 1}`}
              aria-current={activeIndex === i}
              className={`relative h-16 w-16 shrink-0 overflow-hidden rounded-lg border-2 transition-colors ${activeIndex === i ? 'border-[var(--color-primary,#111)]' : 'border-transparent hover:border-gray-300'}`}
            >
              <Image
                src={img.url}
                alt={img.alt_text ?? `Miniatura ${i + 1}`}
                fill
                sizes="64px"
                className="object-cover"
              />
            </button>
          ))}
        </div>
      )}
    </div>
  )
}
