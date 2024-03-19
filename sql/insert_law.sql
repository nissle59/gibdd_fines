INSERT INTO
			public.law(
				id,         -- KoAPcode
                number,
			    part,
                law_description,      -- KoAPtext
			    law_part_description  -- KoAPtext
			)
		VALUES (
			$1, $2, $3,
		    $4,
		    $4
		)
		on conflict (id)
		do update set law_description      = $4,
                      law_part_description = $4
		RETURNING
			id,
            law_part_description