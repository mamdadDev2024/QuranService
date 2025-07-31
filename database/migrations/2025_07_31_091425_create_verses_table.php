<?php

use App\Models\Hizb;
use App\Models\Page;
use App\Models\Surah;
use Illuminate\Database\Migrations\Migration;
use Illuminate\Database\Schema\Blueprint;
use Illuminate\Support\Facades\Schema;

return new class extends Migration
{
    /**
     * Run the migrations.
     */
    public function up(): void
    {
        Schema::create('verses', function (Blueprint $table) {
            $table->id();
            $table->biginteger('global_number')->unique();
            $table->biginteger('local_number');
            $table->foreignIdFor(Surah::class)->constrained('surahs')->cascadeOnDelete();
            $table->foreignIdFor(Hizb::class)->constrained('hizbs')->cascadeOnDelete();
            $table->foreignIdFor(Page::class)->constrained('pages')->cascadeOnDelete();
            $table->timestamps();
        });
    }

    /**
     * Reverse the migrations.
     */
    public function down(): void
    {
        Schema::dropIfExists('verses');
    }
};
