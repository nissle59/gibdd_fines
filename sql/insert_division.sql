INSERT INTO
			fines_base.divisions(
				id,
			    name
			)
VALUES ($1::int4,
                $2::text
		)
		on conflict (id)
		do update set name = $2::text
		RETURNING
			id,
            name