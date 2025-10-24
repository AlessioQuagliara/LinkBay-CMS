import app from '@adonisjs/core/services/app'
import { HttpContext, ExceptionHandler } from '@adonisjs/core/http'

export default class HttpExceptionHandler extends ExceptionHandler {
  /**
   * In debug mode, the exception handler will display verbose errors
   * with pretty printed stack traces.
   */
  protected debug = !app.inProduction

  /**
   * The method is used for handling errors and returning
   * response to the client
   */
  async handle(error: unknown, ctx: HttpContext) {
    // Handle database errors
    if (error && typeof error === 'object' && 'code' in error) {
      const dbError = error as any

      // Handle unique constraint violations
      if (dbError.code === '23505') {
        return ctx.response.status(409).json({
          success: false,
          error: {
            message: 'Resource already exists',
            code: 'DUPLICATE_ENTRY'
          }
        })
      }

      // Handle foreign key constraint violations
      if (dbError.code === '23503') {
        return ctx.response.status(400).json({
          success: false,
          error: {
            message: 'Invalid reference',
            code: 'FOREIGN_KEY_VIOLATION'
          }
        })
      }
    }

    return super.handle(error, ctx)
  }

  /**
   * The method is used to report error to the logging service or
   * the third party error monitoring service.
   *
   * @note You should not attempt to send a response from this method.
   */
  async report(error: unknown, ctx: HttpContext) {
    return super.report(error, ctx)
  }
}
