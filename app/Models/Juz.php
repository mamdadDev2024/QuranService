<?php

namespace App\Models;

use Illuminate\Database\Eloquent\Model;

class Juz extends Model
{
    protected $fillable = [
        'number',
        'text'
    ];

    public function verses()
    {
        return $this->hasMany(Verse::class);
    }
}
