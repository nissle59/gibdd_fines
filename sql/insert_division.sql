INSERT INTO
			fines_base.divisions(
				id,
			    name
			)
		VALUES (
			$1,
		    $2
		)
		on conflict (id)
		do update set
		    name = $2
		RETURNING
			id,
            name