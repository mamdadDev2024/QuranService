<?php

namespace App\Models;

use Illuminate\Database\Eloquent\Model;

class Word extends Model
{
    public function verse()
    {
        return $this->belongsTo(Word::class);
    }
}
