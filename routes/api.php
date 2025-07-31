<?php

use Illuminate\Http\Request;
use Illuminate\Support\Facades\Route;
use App\Http\Controllers\Api\Quran\SurahController;
use App\Http\Controllers\Api\Quran\VerseController;
use App\Http\Controllers\V1\GetByPageController;

Route::middleware('auth:sanctum')->get('/user', function (Request $request) {
    return $request->user();
});

Route::prefix('quran')->as('quran.')->group(function () {
    // Route::get('/surahs', [SurahController::class, 'index'])->name('surahs.index');
    
    // Route::get('/surahs/{id}', [SurahController::class, 'show'])->name('surahs.show');

    // Route::get('/surahs/{id}/verses', [VerseController::class, 'index'])->name('verses.index');

    // Route::get('/verses/{id}', [VerseController::class, 'show'])->name('verses.show');

    // Route::get('pages' , IndexPageController::class)->name('page.index');

    Route::get('page/{Page}' , GetByPageController::class)->name('page.index');

});
