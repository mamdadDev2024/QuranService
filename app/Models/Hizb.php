<?php

namespace App\Models;

use Illuminate\Database\Eloquent\Model;

class Hizb extends Model
{
    
    protected $fillable = [
        'text',
        'number'
    ];

    public function verses()
    {
        return $this->hasMany(Verse::class);
    }

}
