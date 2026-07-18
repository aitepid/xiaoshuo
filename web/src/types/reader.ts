export interface ChapterMeta {
  id: number
  chapter_number: number
  title: string
  volume_title: string
  word_count: number
}

export interface ChapterDetail extends ChapterMeta {
  novel: number
  novel_title: string
  content: string
}
