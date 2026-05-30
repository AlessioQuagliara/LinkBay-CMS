<?php

declare(strict_types=1);

use Illuminate\Database\Migrations\Migration;
use Illuminate\Database\Schema\Blueprint;
use Illuminate\Support\Facades\Schema;

return new class extends Migration
{
    protected $connection = 'central';

    public function up(): void
    {
        Schema::connection('central')->create('platform_fee_rules', function (Blueprint $table) {
            $table->id();
            $table->unsignedBigInteger('plan_id')->nullable();
            $table->string('billing_type', 20)->nullable();   // monthly | yearly | lifetime | null = all
            $table->decimal('fee_pct', 5, 4);                // 0.3000 = 30%
            $table->string('fee_type', 30)->default('platform_share'); // platform_share | transaction_fee
            $table->timestamp('valid_from');
            $table->timestamp('valid_until')->nullable();
            $table->string('description')->nullable();
            $table->unsignedBigInteger('created_by_user_id')->nullable();
            $table->timestamp('created_at')->useCurrent();
            // NO updated_at — append-only, immutable

            $table->foreign('plan_id')->references('id')->on('plans')->onDelete('cascade');
            $table->foreign('created_by_user_id')->references('id')->on('users')->onDelete('set null');

            $table->index(['plan_id', 'billing_type', 'valid_from']);
        });
    }

    public function down(): void
    {
        Schema::connection('central')->dropIfExists('platform_fee_rules');
    }
};
