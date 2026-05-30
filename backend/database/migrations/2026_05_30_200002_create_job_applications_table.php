<?php

use Illuminate\Database\Migrations\Migration;
use Illuminate\Database\Schema\Blueprint;
use Illuminate\Support\Facades\Schema;

return new class extends Migration
{
    protected $connection = 'central';

    public function up(): void
    {
        Schema::connection('central')->create('job_applications', function (Blueprint $table) {
            $table->id();
            $table->foreignId('job_position_id')
                ->constrained('job_positions')
                ->cascadeOnDelete();
            $table->string('full_name', 150);
            $table->string('email', 255);
            $table->string('phone', 50)->nullable();
            $table->string('location', 150)->nullable();
            $table->string('linkedin_url', 500)->nullable();
            $table->string('portfolio_url', 500)->nullable();
            $table->text('motivation');
            $table->text('experience_summary');
            $table->string('cv_path', 500);
            $table->enum('status', ['new', 'reviewing', 'shortlisted', 'rejected', 'closed'])->default('new');
            $table->text('admin_notes')->nullable();
            $table->string('ip_address', 45)->nullable();
            $table->timestamps();
        });
    }

    public function down(): void
    {
        Schema::connection('central')->dropIfExists('job_applications');
    }
};
