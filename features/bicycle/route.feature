@routing @bicycle @route
Feature: Bike -  Test route parsing

    Background:
        Given the profile "bicycle"

    Scenario: Bike - Prefer routes 
        Given the node map
        | a |  |   |   |  | b |
        |   |  | c | d |  |   |

        And the ways
        | nodes |
        | ab    |
        | ac    |
        | cd    |
        | db    |

        And the relations
        | type  | route   | name        | network | way:route |
        | route | bicycle | Green Route | lcn     | ac,cd,db  |

        When I route I should get
        | from | to | route    |
        | a    | b  | ac,cd,db |

    Scenario: Bike - Prefer routes 2
        Given the node map
        | a | b | c |
        | d | e | f |
        | g | h | i |

        And the ways
        | nodes |
        | gh    |
        | be    |
        | eh    |
        | cf    |
        | ab    |
        | bc    |
        | hi    |
        | ad    |
        | dg    |
        | de    |
        | ef    |
        | fi    |

        And the relations
        | type  | route   | name | network | way:route |
        | route | bicycle | r    | lcn     | gh,bc     |

        When I route I should get
        | from | to | route       |
        | a    | f  | ab,bc,cf    |
        | i    | d  | hi,gh,dg    |
        | c    | g  | bc,be,eh,gh |

    Scenario: Bike - Use route name for unnamed ways 
        Given the node map
        | a |  |   |   |  | b |
        |   |  | c | d |  |   |

        And the ways
        | nodes | name  |
        | ac    | ac    |
        | cd    | (nil) |
        | db    | db    |

        And the relations
        | type  | route   | name        | network | way:route |
        | route | bicycle | Green Route | lcn     | ac,cd,db  |

        When I route I should get
        | from | to | route             |
        | a    | b  | ac,Green Route,db |
