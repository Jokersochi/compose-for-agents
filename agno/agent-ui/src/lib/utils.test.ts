import { describe, it } from 'node:test'
import assert from 'node:assert'
import { cn, truncateText, isValidUrl, getJsonMarkdown } from './utils'

describe('utils', () => {
  describe('cn', () => {
    it('should merge class names correctly', () => {
      assert.strictEqual(cn('text-red-500', 'bg-blue-500'), 'text-red-500 bg-blue-500')
    })

    it('should handle conditional classes', () => {
      assert.strictEqual(cn('base', true && 'active', false && 'inactive'), 'base active')
    })

    it('should handle array of classes', () => {
      assert.strictEqual(cn(['text-red-500', 'bg-blue-500']), 'text-red-500 bg-blue-500')
    })

    it('should resolve tailwind conflicts', () => {
      // Note: This test expects twMerge behavior
      assert.strictEqual(cn('p-2', 'p-4'), 'p-4')
    })

    it('should handle null, undefined and boolean values', () => {
      assert.strictEqual(cn('base', null, undefined, true, false), 'base')
    })
  })

  describe('truncateText', () => {
    it('should truncate text longer than the limit with two dots', () => {
      assert.strictEqual(truncateText('Hello World', 5), 'Hello..')
    })

    it('should not truncate text shorter than or equal to the limit', () => {
      assert.strictEqual(truncateText('Hello', 10), 'Hello')
      assert.strictEqual(truncateText('Hello', 5), 'Hello')
    })

    it('should return empty string for empty input', () => {
      assert.strictEqual(truncateText('', 5), '')
    })
  })

  describe('isValidUrl', () => {
    it('should return true for valid http urls', () => {
      assert.strictEqual(isValidUrl('http://example.com'), true)
    })

    it('should return true for valid https urls', () => {
      assert.strictEqual(isValidUrl('https://example.com/path?query=1'), true)
    })

    it('should return true for localhost', () => {
      assert.strictEqual(isValidUrl('http://localhost:3000'), true)
    })

    it('should return true for IP addresses', () => {
      assert.strictEqual(isValidUrl('http://192.168.1.1'), true)
    })

    it('should return false for invalid urls', () => {
      assert.strictEqual(isValidUrl('not-a-url'), false)
      assert.strictEqual(isValidUrl('ftp://example.com'), false)
      assert.strictEqual(isValidUrl('://example.com'), false)
    })
  })

  describe('getJsonMarkdown', () => {
    it('should return formatted json markdown', () => {
      const obj = { foo: 'bar' }
      const expected = '```json\n{\n  "foo": "bar"\n}\n```'
      assert.strictEqual(getJsonMarkdown(obj), expected)
    })

    it('should handle empty object', () => {
      const expected = '```json\n{}\n```'
      assert.strictEqual(getJsonMarkdown({}), expected)
    })

    it('should handle circular references gracefully', () => {
      const obj: any = { a: 1 }
      obj.self = obj
      const result = getJsonMarkdown(obj)
      assert.ok(result.startsWith('```\n'))
    })
  })
})
