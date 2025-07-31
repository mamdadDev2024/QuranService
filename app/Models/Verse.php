<?php

namespace App\Models;

use Illuminate\Database\Eloquent\Model;

class Verse extends Model
{
    public function words()
    {
        return $this->hasMany(Word::class);
    }

    public function page()
    {
        return $this->belongsTo(Page::class);
    }

    public function surah()
    {
        return $this->belongsTo(Surah::class);
    }

    public function juzs()
    {
        return $this->belongsTo(Juz::class);
    }
}
